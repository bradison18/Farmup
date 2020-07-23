from django.urls import path ,include
from django.conf import settings
from . import views

app_name='tracking'
urlpatterns = [
    path('',views.track,name='track'),
    path('change/',views.change_status,name='change')
]