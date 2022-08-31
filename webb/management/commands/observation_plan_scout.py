from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from webb.models import Report
import requests


def check_multiple_cycles(element_list):
    """Check the number of occurrences.

    If given list contain only one value,
    I expect that the cycle 1 is still in progress
    and no action is needed.

    If given list contain more values than 1,
    perhaps that could mean cycle 2 has started.
    The e-mail will be sent to inform that needs
    to be done some changes in the code to adapt
    the app. The command will be stopped.
    """

    if len(element_list) > 1:
        # TODO: Send warning email
        raise CommandError('Error: Multiple cycles are suspected. The element has appeared more times than expected.')

class Command(BaseCommand):
    help = 'Scrape urls that contains report text files and downloads them to a predetermined folder.'

    def handle(self, *args, **options):

        base_url = 'https://www.stsci.edu'
        #url = base_url + '/jwst/science-execution/observing-schedules'
        #response = requests.get(url)
        #soup = BeautifulSoup(response.content)

        # I download the page so I don't scrape it everytime during the development
        url = 'source_data/OBSERVING_SCHEDULES.htm'

        with open(url, "r", encoding="utf-8") as f:
            html = f.read()

            soup = BeautifulSoup(html, 'html.parser')
            main_content = soup.find(id='main-content')
            tablist = main_content.find_all('div', role='tablist')

            if len(tablist) == 0:
                raise CommandError('Error: Div with role=tablist not found.')

            check_multiple_cycles(tablist)


            # I. Scraping the title (cycle number)
            title = tablist[0].find_all('span', class_='accordion__title-text')

            if len(title) == 0:
                raise CommandError('Error: Title not found.')

            check_multiple_cycles(title)
            title_cycle = title[0].text.split(' ')
            cycle_number = title_cycle[1]


            # II. Scraping report links
            links = tablist[0].find_all('a')
            
            saved_reports = Report.objects.filter(cycle=cycle_number).values_list('package_number', flat=True)

            for link in reversed(links):

                file_name = link['href'].split('/')[-1]
                package_number = file_name.split('_')[0]

                if package_number in saved_reports:
                    # Skip reports that are already saved
                    continue

                # Saving report file
                data_source_url = base_url + link['href']
                target_path = 'source_data/cycle_%s/%s' % (cycle_number, file_name)

                r = requests.get(data_source_url)
                open(target_path, 'wb').write(r.content)

                # Saving headinfo to model Report
                report = Report(
                    package_number = package_number,
                    date_code = file_name.split('_')[2].replace('.txt', ''),
                    cycle = cycle_number
                )
                report.save()


            # Notes:
            # - If directory 'source_data' or 'cycle_*' does not exist -> create