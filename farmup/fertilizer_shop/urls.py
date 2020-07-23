
from django.conf.urls import url
from django.urls import path,include
from . import views

app_name = "fertilizer_shop"


urlpatterns = [
    path('addfertilizer',views.addfertilizer,name="addfertilizer"),
    path('createnew',views.createnew,name="createnew"),
    path('shop',views.shop,name="shop"),
    path('iteminfo/<id>',views.iteminfo,name='iteminfo')
]
