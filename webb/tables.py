import django_tables2 as tables
from .models import Visit


class ObservingScheduleTable(tables.Table):

    class Meta:
        model = Visit
        fields = ('visit_id', 'scheduled_start_time', 'duration', 'target_name', 'category', 'keywords')
        attrs = {'class': "table table-dark table-hover"}
        row_attrs = {
            'class': lambda record: 'underway' if record.is_underway else ''
        }
