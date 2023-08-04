from django.core.management.base import BaseCommand
from django.db import IntegrityError
from webb.models import Report
from bs4 import BeautifulSoup
from decouple import config
import requests
import logging
import re
import os


BASE_URL = 'https://www.stsci.edu'
TARGET_URL = BASE_URL + '/jwst/science-execution/observing-schedules'

logger = logging.getLogger(__name__)


def get_package_number(file_content):
    """
    Report file contains package number on the first line.
    """
    lines = file_content.text.split('\n')
    return lines[0].replace('\n', '').split(' ')[-1]


def save_report_file(cycle_number, file_name, content):
    """
    Saves the report file to the source_data folder and a subfolder
    with a specific cycle number.
    If the cycle folder does not exist it will be created.
    """
    folder = f'source_data/cycle_{cycle_number}'
    target_path = f'{folder}/{file_name}'

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    with open(target_path, 'wb') as writer:
        writer.write(content)


def get_site_content():
    """
    This function prevents scraping the real site during development purposes.

    If the target site is saved locally and url to the file defined in the environment
    file as LOCAL_TARGET_URL, the function returns content of the saved file.
    Otherwise, returns the content of the real target site.
    """
    local_target_url = config('LOCAL_TARGET_URL', default=None)

    if local_target_url:
        with open(local_target_url, 'r', encoding='utf-8') as f:
            html = f.read()
    else:
        response = requests.get(TARGET_URL)
        html = response.content

    return BeautifulSoup(html, 'html.parser')


class Command(BaseCommand):
    help = 'Scrapes url that contains report text files and downloads them to a predetermined folder.'

    def handle(self, *args, **options):

        logger.info('Scout started to work.')

        content = get_site_content()
        cycle_headers = content.find_all(
            'button',
            {'aria-label': re.compile('Cycle [0-9]+')}
        )

        for head in reversed(cycle_headers):

            cycle_number = head['aria-label'].split(' ')[1]
            cycle_body = content.find('div', {'aria-labelledby': head['id']})
            links = cycle_body.find_all('a')

            stored_reports = Report.objects.filter(
                cycle=cycle_number).values_list('file_name', flat=True)

            for link in reversed(links):

                report_file_name = link['href'].split('/')[-1]
                file_name = report_file_name.split('.')[0]

                if file_name in stored_reports:
                    # Skip reports that are already stored
                    continue

                logger.info(f'Report file found: {report_file_name}')

                report_file = requests.get(BASE_URL + link['href'])
                package_number = get_package_number(report_file)

                # Save heading to model Report
                try:
                    report = Report(
                        file_name=file_name,
                        package_number=package_number,
                        date_code=file_name.split('_report_')[1],
                        cycle=cycle_number
                    )
                    report.save()
                except IntegrityError:
                    logger.warning(f'The report with this package number '
                                   f'"{package_number}" is already saved.')
                    break

                # Save report file
                save_report_file(cycle_number, report_file_name, report_file.content)
                logger.info('Report file saved.')

        logger.info('Scout finished the work.')
