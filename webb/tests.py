from django.test import TestCase
from django.urls import reverse
from .models import Report, Visit
from .management.commands.report_parser import get_instrument_type,format_duration,format_start_time,get_column_lengths,get_type_of_report
import datetime


class WebbTests(TestCase):

    def setUp(self):
        r = Report.objects.create(package_number='2219105f02', date_code='20220710', cycle=1)

        Visit.objects.create(report=r, visit_id='2739:4:1', scheduled_start_time='2022-07-14T19:00:00Z', duration=format_duration('00/00:12:06'), target_name='Neptune', keywords='Planet')
        Visit.objects.create(report=r, visit_id='1022:9:5', scheduled_start_time='2022-07-15T19:00:00Z', duration=format_duration('00/00:12:06'), target_name='Jupiter', keywords='Planet')

    def test_url_exists_at_correct_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Webb is observing..')

class ReportParserTests(TestCase):

    def setUp(self):
        r = Report.objects.create(package_number='2219105f02', date_code='20220710', cycle=1)

        Visit.objects.create(report=r, visit_id='2739:4:1', scheduled_start_time='2022-07-14T19:00:00Z', duration=format_duration('00/00:12:06'), target_name='Neptune', keywords='Planet')
        Visit.objects.create(report=r, visit_id='1022:9:5', scheduled_start_time='2022-07-15T19:00:00Z', duration=format_duration('00/00:12:06'), target_name='Jupiter', keywords='Planet')

    def test_get_instrument_type(self):

        self.assertEqual(get_instrument_type('NIRCam Imaging'), '1')
        self.assertEqual(get_instrument_type('NIRSpec Dark'), '2')
        self.assertEqual(get_instrument_type('MIRI External Flat'), '3')
        self.assertEqual(get_instrument_type('NIRISS Single-Object Slitless Spectroscopy'), '4')
        self.assertEqual(get_instrument_type('WFSC NIRCam Fine Phasing'), '1')
        self.assertEqual(get_instrument_type('Station Keeping'), None)
        self.assertEqual(get_instrument_type('FGS Internal Flat'), None)
        self.assertEqual(get_instrument_type(''), None)

    def test_format_start_time(self):

        self.assertEqual(format_start_time('2022-07-10T13:23:07Z'), '2022-07-10T13:23:07Z')
        self.assertEqual(format_start_time('2022-07-10'), None)
        self.assertEqual(format_start_time('some date and time'), None)
        self.assertEqual(format_start_time(''), None)

    def test_format_duration(self):

        self.assertEqual(format_duration('00/00:16:55'), datetime.timedelta(minutes=16, seconds=55))
        self.assertEqual(format_duration('01/17:24:00'), datetime.timedelta(days=1, hours=17, minutes=24, seconds=0))
        self.assertEqual(format_duration(''), None)

    def test_get_column_lengths(self):

        self.assertEqual(get_column_lengths('----------  -------  -----------'), [10, 7, 11])
        self.assertEqual(get_column_lengths('-  --  ---  ----  -----'), [1, 2, 3, 4, 5])
        self.assertEqual(get_column_lengths('------'), [6])
        self.assertEqual(get_column_lengths(''), [0])

    def test_get_type_of_report(self):
        
        self.assertEqual(get_type_of_report('2022-07-16T22:00:00Z'), 'new')
        self.assertEqual(get_type_of_report('2022-07-14T22:00:00Z'), 'update')
        self.assertEqual(get_type_of_report('This is not date time'), None)
        self.assertEqual(get_type_of_report(''), None)