from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from webb.models import Report
import requests
import re


class Command(BaseCommand):
    help = 'Scrape urls that contains report text files and download them to a predetermined folder.'

    def handle(self, *args, **options):

        base_url = 'https://www.stsci.edu'
        #url = base_url + '/jwst/science-execution/observing-schedules'
        #response = requests.get(url)
        #soup = BeautifulSoup(response.content, 'html.parser')

        # I download the page so I don't scrape it everytime during the development
        url = 'source_data/OBSERVING_SCHEDULES.htm'

        with open(url, 'r', encoding='utf-8') as f:
            html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            cycle_headers = soup.find_all('button', {'aria-label':re.compile('Cycle [0-9]+')})

            for head in cycle_headers:

                cycle_number = head['aria-label'].split(' ')[1]
                cycle_body = soup.find('div', {'aria-labelledby': head['id']})
                links = cycle_body.find_all('a')

                saved_reports = Report.objects.filter(cycle=cycle_number).values_list('package_number', flat=True)

                for link in reversed(links):

                    file_name = link['href'].split('/')[-1]
                    package_number = file_name.split('_')[0]

                    if package_number in saved_reports:
                        # Skip reports that are already saved
                        continue

                    # Save report file
                    data_source_url = base_url + link['href']
                    target_path = 'source_data/cycle_%s/%s' % (cycle_number, file_name)

                    r = requests.get(data_source_url)
                    open(target_path, 'wb').write(r.content)

                    # Save headinfo to model Report
                    report = Report(
                        package_number = package_number,
                        date_code = file_name.split('_')[2].replace('.txt', ''),
                        cycle = cycle_number
                    )
                    report.save()
                    break # for dev purposes I use only one loop per run

# TODO:
# - If directory 'source_data' or 'cycle_*' does not exist -> create