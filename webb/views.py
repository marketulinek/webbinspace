from django.shortcuts import render
from django.utils import timezone
from .models import Visit


def homepage(request):

    prev_current_target = Visit.objects.filter(scheduled_start_time__lte=timezone.now()).order_by('-scheduled_start_time')[:2]
    next_target = Visit.objects.filter(scheduled_start_time__gte=timezone.now()).order_by('scheduled_start_time')[:1]

    context = {
        'prev_target': prev_current_target[0],
        'current_target': prev_current_target[1],
        'next_target': next_target
    }

    return render(request, 'home.html', context)