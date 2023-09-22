from django.test import TestCase
from django.urls import reverse
from .models import Report, Category, Visit
from .management.commands.report_parser import get_instrument_type, format_duration, get_column_lengths, \
    get_type_of_report, find_line_order_with_hyphens
import datetime


class WelcomeTests(TestCase):

    def test_homepage_without_data(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 302)

    def test_url_exists_at_correct_location(self):
        response = self.client.get('/welcome/')
        self.assertEqual(response.status_code, 200)

    def test_welcome(self):
        response = self.client.get(reverse('welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'welcome_contributor.html')
        self.assertContains(response, 'Hello Space!')


class WebbTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.report = Report.objects.create(
            file_name='2219105f02_report_20220710', report_code='2219105f02_20220710',
            package_number='2219105f02', date_code='20220710', cycle=1)

        cls.report_two = Report.objects.create(
            file_name='20230423_report_20230421', report_code='2311308f03_20230421',
            package_number='2311308f03', date_code='20230421', cycle=1)

        cls.category = Category.objects.create(name='Solar System')

        cls.visit_one = Visit.objects.create(report=cls.report,
                                             visit_id='2739:4:1',
                                             scheduled_start_time='2022-07-14T19:00:00Z',
                                             duration=format_duration('00/00:12:06'),
                                             target_name='Neptune',
                                             category=cls.category,
                                             keywords='Planet')

        cls.visit_two = Visit.objects.create(report=cls.report,
                                             visit_id='1022:9:5',
                                             scheduled_start_time='2022-07-15T19:00:00Z',
                                             duration=format_duration('00/00:12:06'),
                                             target_name='Jupiter',
                                             keywords='Planet')

    def test_report_model(self):
        self.assertEqual(self.report.file_name, '2219105f02_report_20220710')
        self.assertEqual(self.report.report_code, '2219105f02_20220710')
        self.assertEqual(self.report.package_number, '2219105f02')
        self.assertEqual(self.report.date_code, '20220710')
        self.assertEqual(self.report.cycle, 1)

    def test_category_model(self):
        self.assertEqual(self.category.name, 'Solar System')

    def test_visit_model(self):
        self.assertEqual(self.visit_one.report.file_name, '2219105f02_report_20220710')
        self.assertEqual(self.visit_one.visit_id, '2739:4:1')
        self.assertEqual(self.visit_one.scheduled_start_time, '2022-07-14T19:00:00Z')
        self.assertEqual(self.visit_one.duration, datetime.timedelta(minutes=12, seconds=6))
        self.assertEqual(self.visit_one.target_name, 'Neptune')
        self.assertEqual(self.visit_one.category.name, 'Solar System')
        self.assertEqual(self.visit_one.keywords, 'Planet')
        self.assertEqual(self.visit_one.valid, True)

    def test_url_exists_at_correct_location_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Webb is observing..')

    def test_url_exists_at_correct_location_statistics_view(self):
        response = self.client.get('/statistics/')
        self.assertEqual(response.status_code, 200)

    def test_statistics_view(self):
        response = self.client.get(reverse('statistics'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'statistics.html')
        self.assertContains(response, 'Statistics on the time spent observing')

    def test_url_exists_at_correct_location_observingschedule_listview(self):
        response = self.client.get('/observing-schedules/')
        self.assertEqual(response.status_code, 200)

    def test_observingschedule_listview(self):
        response = self.client.get(reverse('observing_schedules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'observation_schedule.html')
        self.assertContains(response, 'Observing Schedules')

    def test_url_exists_at_correct_location_report_listview(self):
        response = self.client.get('/reports/cycle-1/')
        self.assertEqual(response.status_code, 200)

    def test_report_listview(self):
        response = self.client.get(reverse('report_list', kwargs={'cycle_number': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report_list.html')
        self.assertContains(response, 'Report List')
        # Report with zero visits
        self.assertContains(response, 'Empty!')


class ReportParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.report = Report.objects.create(package_number='2219105f02', date_code='20220710',
                                           report_code='2219105f02_20220710', cycle=1)

        cls.visit_one = Visit.objects.create(report=cls.report, visit_id='2739:4:1',
                                             scheduled_start_time='2022-07-14T19:00:00Z',
                                             duration=format_duration('00/00:12:06'),
                                             target_name='Neptune', keywords='Planet')
        cls.visit_two = Visit.objects.create(report=cls.report, visit_id='1022:9:5',
                                             scheduled_start_time='2022-07-15T19:00:00Z',
                                             duration=format_duration('00/00:12:06'),
                                             target_name='Jupiter', keywords='Planet')

    def test_get_instrument_type(self):
        self.assertEqual(get_instrument_type('NIRCam Imaging'), '1')
        self.assertEqual(get_instrument_type('NIRSpec Dark'), '2')
        self.assertEqual(get_instrument_type('MIRI External Flat'), '3')
        self.assertEqual(get_instrument_type('NIRISS Single-Object Slitless Spectroscopy'), '4')
        self.assertEqual(get_instrument_type('WFSC NIRCam Fine Phasing'), '1')
        self.assertEqual(get_instrument_type('Station Keeping'), None)
        self.assertEqual(get_instrument_type('FGS Internal Flat'), None)
        self.assertEqual(get_instrument_type(''), None)

    def test_format_duration(self):
        self.assertEqual(format_duration('00/00:16:55'), datetime.timedelta(minutes=16, seconds=55))
        self.assertEqual(format_duration('01/17:24:00'), datetime.timedelta(days=1, hours=17, minutes=24, seconds=0))
        self.assertEqual(format_duration(''), None)

    def test_find_line_order_with_hyphens(self):
        self.assertEqual(find_line_order_with_hyphens(['OP Package', '', 'VISIT ID', '-------------']), 3)
        self.assertEqual(find_line_order_with_hyphens(['\n', 'VISIT ID\n', '-------------\n']), 2)
        self.assertEqual(find_line_order_with_hyphens(['----\n']), 0)
        self.assertEqual(find_line_order_with_hyphens(['\n']), 0)
        self.assertEqual(find_line_order_with_hyphens([]), 0)

    def test_get_column_lengths(self):
        self.assertEqual(get_column_lengths('----------  -------  -----------'), [10, 7, 100])
        self.assertEqual(get_column_lengths('-  --  ---  ----  -----'), [1, 2, 3, 4, 100])
        self.assertEqual(get_column_lengths('------'), [100])
        self.assertEqual(get_column_lengths(''), [100])

    def test_get_type_of_report(self):
        self.assertEqual(get_type_of_report('2022-07-16T22:00:00Z'), 'new')
        self.assertEqual(get_type_of_report('2022-07-14T22:00:00Z'), 'update')
        self.assertEqual(get_type_of_report('This is not date time'), None)
        self.assertEqual(get_type_of_report(''), None)
