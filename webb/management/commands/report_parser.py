from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db import IntegrityError
from webb.models import Report, Visit, Category
import datetime as dt
import logging


logger = logging.getLogger(__name__)


def get_files_to_parse():
    """
    It searches for reports that don't have visits in the database yet.
    These reports were saved in specific folder by Scout and are still
    waiting to be parsed and their information saved into database.
    """
    return Report.objects.annotate(num_visits=Count('visits')).filter(num_visits=0).order_by('date_code')

def line_to_list(line, column_lengths):

    data_list = list()
    begin_char_key = -2
    for column_len in column_lengths:

        begin_char_key += 2
        end_char_key = begin_char_key + column_len
        data_list.append(line[begin_char_key:end_char_key].strip())
        begin_char_key += column_len

    return data_list

def get_column_lengths(line):

    value_list = list()
    for value in line.replace('\n', '').split('  '):
        value_list.append(len(value))

    return value_list

def merge_lists_to_dict(key_list, value_list):

    new_dict = dict()
    for index, key in enumerate(key_list):
        new_dict[key] = value_list[index]

    return new_dict

def add_category_if_not_exists(category_name):

    if category_name:
        category, created = Category.objects.get_or_create(name=category_name)
        return category

    return None

def format_start_time(time):

    try:
        dt.datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
        return time
    except ValueError:
        return None

def format_duration(duration):

    if duration:
        days,time = duration.split('/')
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

    visit = Visit(
        report = report,
        visit_id = data['VISIT ID'],
        pcs_mode = data['PCS MODE'],
        visit_type = data['VISIT TYPE'],
        scheduled_start_time = format_start_time(data['SCHEDULED START TIME']),
        duration = format_duration(data['DURATION']),
        science_instrument_and_mode = data['SCIENCE INSTRUMENT AND MODE'],
        instrument = get_instrument_type(data['SCIENCE INSTRUMENT AND MODE']),
        target_name = data['TARGET NAME'],
        category = add_category_if_not_exists(data['CATEGORY']),
        keywords = data['KEYWORDS'],
    )
    visit.save()

class Command(BaseCommand):
    help = 'Parse chosen report file and save data into database.'

    def handle(self, *args, **options):

        logger.info('Report parser started to work.')

        for report in get_files_to_parse():

            logger.info('Parsing the report: %s', report.file_name)

            with open(report.get_path_to_file(), 'r') as reader:

                lines = reader.readlines()

                column_lengths = get_column_lengths(lines[3])
                column_names = line_to_list(lines[2], column_lengths)

                for line_number, line in enumerate(lines):

                    if line_number > 3:

                        data_list = line_to_list(line, column_lengths)
                        data = merge_lists_to_dict(column_names, data_list)

                        if len(data) > 0 and data['VISIT ID']:

                            try:
                                save_data(report, data)
                            except IntegrityError:
                                logger.exception('This visit ID %s is already saved in the database.', data['VISIT ID'])

            logger.info('Parsed.')
            break # limited number loops for dev purposes

        logger.info('Report parser finished the work.')