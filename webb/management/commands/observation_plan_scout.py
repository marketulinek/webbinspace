from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
from webb.models import Report
import requests


# TODO: function that will send warning email and raise CommandError

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

            if len(tablist) > 1:
                # Currently there is only one element with 'role=tablist',
                # but I expected second one next year after the cycle 2 will start
                print('Warning: more cycles?')
                # TODO: Send warning email and stop the command
                raise CommandError('Error: Manual check needed.')


            # I. Scraping the title (cycle number)
            title = tablist[0].find_all('span', class_='accordion__title-text')

            if len(title) == 0:
                raise CommandError('Error: Title not found.')

            if len(title) > 1:
                # The same as 'tablist', I expect to find more titles after the cycle 2 will start
                print('Warning: more cycles?')
                # TODO: Send warning email and stop the command
                raise CommandError('Error: Manual check needed.')

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