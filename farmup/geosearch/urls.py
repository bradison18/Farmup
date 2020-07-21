
from django.conf.urls import url
from django.urls import path,include
from . import views
from django.conf.urls import url
app_name = "geosearch"

urlpatterns = [
    path('map_search/',views.gmaps,name='map_search'),
    path('get_address/',views.get_address,name="get_address")
    ]
