from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Visit
from .utils import get_observing_progress
from .filters import VisitFilter
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
import webb.tables as tables


def homepage(request):

    prev_current_target = Visit.objects.filter(
        scheduled_start_time__lte=timezone.now(),
        valid=True).order_by('-scheduled_start_time')[:2]

    if len(prev_current_target) < 2:
        return redirect('welcome')

    prev_target = prev_current_target[1]
    current_target = prev_current_target[0]

    next_target = Visit.objects.filter(
        scheduled_start_time__gte=timezone.now(),
        valid=True).order_by('scheduled_start_time').first()

    current_target_progress = get_observing_progress(
        current_target.scheduled_start_time,
        current_target.duration
    )

    context = {
        'prev_target': prev_target,
        'current_target': current_target,
        'next_target': next_target,
        'current_target_progress': current_target_progress
    }

    return render(request, 'home.html', context)


def welcome_new_contributor(request):
    return render(request, 'welcome_contributor.html')


class ObservingScheduleListView(SingleTableMixin, FilterView):
    model = Visit
    table_class = tables.ObservingScheduleTable
    template_name = 'observation_schedule.html'
    filterset_class = VisitFilter

    def get_queryset(self):
        return Visit.objects.filter(
            scheduled_start_time__isnull=False,
            valid=True).order_by('-scheduled_start_time')
