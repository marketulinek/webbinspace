from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup
import requests


# TODO: function that will send warning email and raise CommandError

class Command(BaseCommand):
    # TODO: Write help

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
            print(cycle_number)


            # II. Scraping report links
            # TODO

            # III.
            # 1) save to model Report (to be aware that it exist)
            # 2) Save .txt file for further data scraping

            # Notes:
            # - If directory 'source_data' or 'cycle_*' does not exist -> create