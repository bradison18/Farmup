
from django.conf.urls import url
from django.urls import path,include
from . import views

app_name = "shopping_cart"

urlpatterns = [
    path('buyingportal/', views.buyingpage, name='buyingpage'),
    path('addCropElements/', views.addCropElements, name='addCropElements'),
    ]