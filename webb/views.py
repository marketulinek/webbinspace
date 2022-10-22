from django.shortcuts import render
from django.utils import timezone
from .models import Visit
from .utils import get_observing_progress


def homepage(request):

    prev_current_target = Visit.objects.filter(scheduled_start_time__lte=timezone.now()).order_by('-scheduled_start_time')[:2]
    prev_target = prev_current_target[1]
    current_target = prev_current_target[0]
    next_target = Visit.objects.filter(scheduled_start_time__gte=timezone.now()).order_by('scheduled_start_time')[:1]

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