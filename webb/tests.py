from django.test import TestCase
from .models import Report, Visit
from .management.commands.report_parser import get_instrument_type,format_duration


class WebbTests(TestCase):

    def setUp(self):
        r = Report.objects.create(package_number='2219105f02', date_code='20220710', cycle=1)

        Visit.objects.create(report=r, visit_id='2739:4:1', scheduled_start_time='2022-07-14T19:00:00Z', duration=format_duration('00/00:12:06'), target_name='Neptune', keywords='Planet')
        Visit.objects.create(report=r, visit_id='1022:9:5', scheduled_start_time='2022-07-15T19:00:00Z', duration=format_duration('00/00:12:06'), target_name='Jupiter', keywords='Planet')

    def test_url_exists_at_correct_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class ReportParserTests(TestCase):

    def test_get_instrument_type(self):

        self.assertEqual(get_instrument_type('NIRCam Imaging'), '1')
        self.assertEqual(get_instrument_type('NIRSpec Dark'), '2')
        self.assertEqual(get_instrument_type('MIRI External Flat'), '3')
        self.assertEqual(get_instrument_type('NIRISS Single-Object Slitless Spectroscopy'), '4')
        self.assertEqual(get_instrument_type('WFSC NIRCam Fine Phasing'), '1')
        self.assertEqual(get_instrument_type('Station Keeping'), None)
        self.assertEqual(get_instrument_type('FGS Internal Flat'), None)
        self.assertEqual(get_instrument_type(''), None)