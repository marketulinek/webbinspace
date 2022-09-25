from django.shortcuts import render
from django.utils import timezone
from .models import Visit
from .utils import get_observing_progress


def homepage(request):

    prev_current_target = Visit.objects.filter(scheduled_start_time__lte=timezone.now()).order_by('-scheduled_start_time')[:2]
    next_target = Visit.objects.filter(scheduled_start_time__gte=timezone.now()).order_by('scheduled_start_time')[:1]

    current_target_progress = get_observing_progress(
        prev_current_target[0].scheduled_start_time,
        prev_current_target[0].duration
    )

    context = {
        'prev_target': prev_current_target[0],
        'current_target': prev_current_target[1],
        'next_target': next_target,
        'current_target_progress': current_target_progress
    }

    return render(request, 'home.html', context)