from django.core.management.base import BaseCommand
from django.db.models import Count
from webb.models import Report, Visit, Category
import datetime as dt


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

def add_category_if_not_exist(category_name):

    try:
        category = Category.objects.get(name=category_name)

    except Category.DoesNotExist:
        category = Category(name=category_name)
        category.save()

    return category

def format_duration(duration):

    days,time = duration.split('/')
    parts_of_time = time.split(':')
    h = int(parts_of_time[0])
    m = int(parts_of_time[1])
    s = int(parts_of_time[2])

    return dt.timedelta(days=int(days), hours=h, minutes=m, seconds=s)

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
        scheduled_start_time = data['SCHEDULED START TIME'],
        duration = format_duration(data['DURATION']),
        science_instrument_and_mode = data['SCIENCE INSTRUMENT AND MODE'],
        instrument = get_instrument_type(data['SCIENCE INSTRUMENT AND MODE']),
        target_name = data['TARGET NAME'],
        category = add_category_if_not_exist(data['CATEGORY']),
        keywords = data['KEYWORDS'],
    )
    visit.save()

class Command(BaseCommand):
    help = 'Parse chosen report file and save data into database.'

    def handle(self, *args, **options):

        for report in get_files_to_parse():

            with open(report.get_path_to_file(), 'r') as reader:

                lines = reader.readlines()

                column_lengths = get_column_lengths(lines[3])
                column_names = line_to_list(lines[2], column_lengths)

                for line_number, line in enumerate(lines):

                    if line_number > 3:

                        data_list = line_to_list(line, column_lengths)
                        data = merge_lists_to_dict(column_names, data_list)

                        if len(data) > 0:
                            save_data(report, data)
                            break

                    if line_number >= 6:
                        break # limited number lines for dev purposes


            break # limited number loops for dev purposes

# Expecting result
{'2222707f03':
    {
        'VISIT ID': '1304:4:1',
        'PCS MODE': 'FINEGUIDE',
        'VISIT TYPE': 'PRIME TARGETED FIXED',
        'SCHEDULED START TIME': '2022-08-15T12:13:43Z',
        'DURATION': '00/00:27:13',
        'SCIENCE INSTRUMENT AND MODE': 'NIRCam Imaging',
        'TARGET NAME': 'SCULPTOR-F0',
        'CATEGORY': 'Galaxy',
        'KEYWORDS': 'Dwarf spheroidal galaxies, Planetary nebulae, ...'
    }
}