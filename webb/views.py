from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import ListView
from .chart import TimeSpentObservingChart
from .filters import VisitFilter
from .models import Report, Category, Visit
from .tables import ObservingScheduleTable
from .utils import get_observing_progress, convert_duration_to_days
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


def homepage(request):

    prev_current_target = Visit.objects.select_related('category').filter(
        scheduled_start_time__lte=timezone.now(),
        valid=True).order_by('-scheduled_start_time')[:2]

    if len(prev_current_target) < 2:
        return redirect('welcome')

    prev_target = prev_current_target[1]
    current_target = prev_current_target[0]

    next_target = Visit.objects.select_related('category').filter(
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


def statistics_view(request):
    return render(request, 'statistics.html')


def category_duration_chart(request):
    categories = Category.objects.annotate(
        total_duration=Sum('visits__duration'))

    labels, tooltips, durations = [], [], []

    for category in categories:
        labels.append(category.name)
        tooltips.append(str(naturaltime(category.total_duration)))
        durations.append(
            convert_duration_to_days(category.total_duration)
        )

    return TimeSpentObservingChart(labels, durations, tooltips).create_json()


def instrument_duration_chart(request):
    instruments = Visit.objects.filter(
        instrument__isnull=False
    ).values('instrument').annotate(total_duration=Sum('duration'))

    labels, tooltips, durations = [], [], []
    instrument_dict = dict((key, value) for key, value in Visit.INSTRUMENT_CHOICES)

    for instrument in instruments:
        labels.append(instrument_dict[instrument['instrument']])
        tooltips.append(str(naturaltime(instrument['total_duration'])))
        durations.append(
            convert_duration_to_days(instrument['total_duration'])
        )

    return TimeSpentObservingChart(labels, durations, tooltips).create_json()


def solarsystem_duration_chart(request):
    solar_system = Visit.objects.filter(
        category__name='Solar System'
    ).values('keywords').annotate(total_duration=Sum('duration'))

    labels, tooltips, durations = [], [], []

    for solsys in solar_system:
        labels.append(solsys['keywords'])
        tooltips.append(str(naturaltime(solsys['total_duration'])))
        durations.append(
            convert_duration_to_days(solsys['total_duration'])
        )

    return TimeSpentObservingChart(labels, durations, tooltips).create_json()


def planet_duration_chart(request):
    planets = ('MERCURY', 'VENUS', 'EARTH', 'MARS', 'JUPITER', 'SATURN', 'URANUS', 'NEPTUNE')
    visits = Visit.objects.filter(category__name='Solar System', keywords='Planet')

    labels, tooltips, durations = [], [], []

    for planet in planets[3:]:
        # Loop from Mars because there are no plans
        # to observe the first three planets.
        planet_qs = visits.filter(
            target_name__icontains=planet
        ).values('keywords').annotate(total_duration=Sum('duration'))

        for planet_data in planet_qs:
            if planet_data is not None:
                labels.append(planet)
                tooltips.append(str(naturaltime(planet_data['total_duration'])))
                durations.append(
                    convert_duration_to_days(planet_data['total_duration'])
                )

    return TimeSpentObservingChart(labels, durations, tooltips).create_json()


class ObservingScheduleListView(SingleTableMixin, FilterView):
    model = Visit
    table_class = ObservingScheduleTable
    template_name = 'observation_schedule.html'
    filterset_class = VisitFilter

    def get_queryset(self):
        return Visit.objects.select_related('category').filter(
            scheduled_start_time__isnull=False,
            valid=True).order_by('-scheduled_start_time')


class ReportListView(ListView):
    model = Report
    template_name = 'report_list.html'
    context_object_name = 'report_list'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(cycle=self.kwargs['cycle_number']).annotate(
            total_number=Count('visits__visit_id')).order_by('-date_code')
