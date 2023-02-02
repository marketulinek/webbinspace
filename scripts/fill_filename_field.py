from django.db.models import CharField, Value as V
from django.db.models.functions import Concat
from webb.models import Report


def run():

    print('Filling in the file name field...')

    Report.objects.all().update(
        file_name=Concat(
            'package_number', V('_report_'), 'date_code', output_field=CharField()
        )
    )

    print('Completed!')
