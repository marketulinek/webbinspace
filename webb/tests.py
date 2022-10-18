from django.test import TestCase
from .management.commands.report_parser import get_instrument_type


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