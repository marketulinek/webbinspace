from django.urls import path
from .views import homepage, welcome_new_contributor


urlpatterns = [
    path('', homepage, name='homepage'),
    path('welcome/', welcome_new_contributor, name='welcome'),
]
