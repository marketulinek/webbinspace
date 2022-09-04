from django.core.management.base import BaseCommand


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

class Command(BaseCommand):
    help = 'Parse chosen report file and save data into database.'

    def handle(self, *args, **options):

        data = dict()
        report_file = 'source_data/cycle_1/2222707f03_report_20220815.txt'

        with open(report_file, 'r') as reader:

            lines = reader.readlines()

            package_number = lines[0].split(' ')[-1].strip()
            column_lengths = get_column_lengths(lines[3])
            column_names = line_to_list(lines[2], column_lengths)

            line_data = list()
            for line_number, line in enumerate(lines):

                if line_number > 3:

                    data_list = line_to_list(line, column_lengths)

                    line_data.append(merge_lists_to_dict(column_names, data_list))

                if line_number >= 6:
                    break # limited number lines for dev purposes

            data[package_number] = line_data

        print(data)

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