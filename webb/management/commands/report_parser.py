from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.utils.dateparse import parse_datetime
from webb.models import Report, Visit, Category
import datetime as dt
import logging


logger = logging.getLogger(__name__)


def get_reports_to_parse():
    """
    Searches for reports that don't have visits in the database yet.

    These reports were saved in specific folder by Scout and are still
    waiting to be parsed and their information saved into database.
    """
    reports_to_parse = Report.objects.annotate(
        num_visits=Count('visits')).filter(num_visits=0).order_by('date_code', 'created_at')

    if len(reports_to_parse) < 1:
        logger.info('No reports to parse.')

    return reports_to_parse


def get_type_of_report(scheduled_start_time):

    scheduled_start_time = parse_datetime(scheduled_start_time)

    if scheduled_start_time is None:
        return None

    latest_visit = Visit.objects.filter(
        scheduled_start_time__isnull=False).order_by('-scheduled_start_time').first()
    if latest_visit is None:
        return None

    if scheduled_start_time > latest_visit.scheduled_start_time:
        return 'new'

    return 'update'


def invalidate_visits_from_datetime(start_time):
    """
    These visits are no longer valid because next report brings updates to the schedule.
    """
    start_time = parse_datetime(start_time)
    return Visit.objects.filter(scheduled_start_time__gte=start_time, valid=True).update(valid=False)


def line_to_list(line, column_lengths):

    data_list = list()
    begin_char_key = -2
    for column_len in column_lengths:

        begin_char_key += 2
        end_char_key = begin_char_key + column_len
        data_list.append(line[begin_char_key:end_char_key].strip())
        begin_char_key += column_len

    return data_list


def find_line_order_with_hyphens(lines):
    """
    Finds the line that contains hyphens for determining
    the length of columns of the report file.

    Returns the order of that line.
    If not found, returns zero.
    """
    for line_order, line in enumerate(lines):
        new_line = line.replace('\n', '')
        if len(new_line) > 0 and all(c in '- ' for c in new_line):
            return line_order

    return 0


def get_column_lengths(line):

    value_list = list()
    for value in line.replace('\n', '').split('  '):
        value_list.append(len(value))

    # The length of the last column in report does not
    # correspond to the number of dashes given.
    # Setting at least 100 characters.
    if value_list[-1] < 100:
        value_list[-1] = 100

    return value_list


def add_category_if_not_exists(category_name):

    if category_name:
        category, _ = Category.objects.get_or_create(name=category_name)
        return category

    return None


def format_duration(duration):

    if duration:
        days, time = duration.split('/')
        parts_of_time = time.split(':')
        h = int(parts_of_time[0])
        m = int(parts_of_time[1])
        s = int(parts_of_time[2])
        return dt.timedelta(days=int(days), hours=h, minutes=m, seconds=s)

    return None


def get_instrument_type(text):

    for choice in Visit.INSTRUMENT_CHOICES:
        if choice[1] in text:
            return choice[0]

    return None


def save_data(report, data):

    Visit.objects.update_or_create(
        visit_id=data['VISIT ID'],
        defaults={
            'report': report,
            'visit_id': data['VISIT ID'],
            'pcs_mode': data['PCS MODE'],
            'visit_type': data['VISIT TYPE'],
            'scheduled_start_time': parse_datetime(data['SCHEDULED START TIME']),
            'duration': format_duration(data['DURATION']),
            'science_instrument_and_mode': data['SCIENCE INSTRUMENT AND MODE'],
            'instrument': get_instrument_type(data['SCIENCE INSTRUMENT AND MODE']),
            'target_name': data['TARGET NAME'],
            'category': add_category_if_not_exists(data['CATEGORY']),
            'keywords': data['KEYWORDS'],
            'valid': True,
        }
    )


class Command(BaseCommand):
    help = 'Parse chosen report file and save data into database.'

    def handle(self, *args, **options):

        logger.info('Report parser started to work.')

        for report in get_reports_to_parse():

            logger.info(f'Parsing the report: {report.file_name}')

            with open(report.get_path_to_file(), 'r') as reader:

                lines = reader.readlines()
                report_type = None

                line_order = find_line_order_with_hyphens(lines)
                if line_order < 1:
                    msg = 'The line used to determine column lengths was not found.'
                    logger.error(msg)
                    raise CommandError(msg)

                column_lengths = get_column_lengths(lines[line_order])
                column_names = line_to_list(lines[line_order-1], column_lengths)

                for line_number, line in enumerate(lines[line_order+1:]):

                    data_list = line_to_list(line, column_lengths)
                    data = dict(zip(column_names, data_list))

                    if len(data) < 1 or not data['VISIT ID']:
                        # Skip if there is no value for VISIT ID
                        # or the dict is empty
                        continue

                    if report_type is None:
                        report_type = get_type_of_report(data['SCHEDULED START TIME'])

                        if report_type == 'update':
                            num_row_updated = invalidate_visits_from_datetime(
                                data['SCHEDULED START TIME'])

                            logger.info('This report file contains updates of the last report.')
                            logger.info(f'{num_row_updated} row(s) has been invalidated.')

                    save_data(report, data)

            logger.info('Parsed.')

        logger.info('Report parser finished the work.')
