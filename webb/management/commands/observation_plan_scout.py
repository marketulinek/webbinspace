from django.core.management.base import BaseCommand
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


def save_report_file(cycle_number, file_name, content):
    """
    Saves the report file to the source_data folder and a subfolder with a specific cycle number.
    If the cycle folder does not exist it will be created.
    """

    folder = 'source_data/cycle_%s' % cycle_number
    target_path = '%s/%s' % (folder, file_name)

    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    
    with open(target_path, 'wb') as writer:
        writer.write(content)

def get_site_content():
    """
    This function prevents scraping the real site during development purposes.

    If the target site is saved locally and url to the file defined in the environment
    file as LOCAL_TARGET_URL, the function returns content of the saved file.
    Otherwise returns the content of the real target site.
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
    help = 'Scrapes urls that contains report text files and downloads them to a predetermined folder.'

    def handle(self, *args, **options):

        logger.info('Scout started to work.')

        content = get_site_content()
        cycle_headers = content.find_all('button', {'aria-label':re.compile('Cycle [0-9]+')})

        for head in cycle_headers:

            cycle_number = head['aria-label'].split(' ')[1]
            cycle_body = content.find('div', {'aria-labelledby': head['id']})
            links = cycle_body.find_all('a')

            saved_reports = Report.objects.filter(cycle=cycle_number).values_list('package_number', flat=True)

            for link in reversed(links):

                file_name = link['href'].split('/')[-1]
                package_number = file_name.split('_')[0]

                if package_number in saved_reports:
                    # Skip reports that are already saved
                    continue

                logger.info('Report file found: %s', file_name)

                # Save report file
                r = requests.get(BASE_URL + link['href'])
                save_report_file(cycle_number, file_name, r.content)
                logger.info('Report file saved.')

                # Save headinfo to model Report
                report = Report(
                    package_number = package_number,
                    date_code = file_name.split('_')[2].replace('.txt', ''),
                    cycle = cycle_number
                )
                report.save()
                break # for dev purposes I use only one loop per command

        logger.info('Scout finished the work.')