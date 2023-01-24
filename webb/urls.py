from django.urls import path
import webb.views as views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('welcome/', views.welcome_new_contributor, name='welcome'),
    path('observing-schedules/', views.ObservingScheduleListView.as_view(), name='observing_schedules'),
    path('observing-schedules/charts/', views.chart_of_observations, name='chart_observations')
]
