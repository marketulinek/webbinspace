from django.urls import path
import webb.views as views


urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('welcome/', views.welcome_new_contributor, name='welcome'),
    path('observing-schedules/', views.ObservingScheduleListView.as_view(), name='observing_schedules'),
    path('statistics/', views.statistics_view, name='statistics'),

    # Charts for statistics
    path('chart/category-duration/', views.category_duration_chart, name='chart_category_duration'),
    path('chart/instrument-duration/', views.instrument_duration_chart, name='chart_instrument_duration'),
    path('chart/solarsystem-duration/', views.solarsystem_duration_chart, name='chart_solarsystem_duration'),
]
