
from django.conf.urls import url
from django.urls import path,include
from . import views

app_name = "crop_selling_portal"

urlpatterns = [
    path('buyingportal/', views.buyingpage, name='buyingpage'),
    ]
