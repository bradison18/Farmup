
from django.conf.urls import url
from django.urls import path,include
from . import views

app_name = "shopping_cart"


urlpatterns = [
    path('buyingportal/', views.buyingpage, name='buyingpage'),
    path('addCropElements/', views.addCropElements, name='addCropElements'),
    path('<slug>/', views.addCropElements, name="add_to_cart"),
    path('buyingportal/cart/',views.checkout,name="cart"),
    path('deleteitems/<item_name>',views.delete_from_cart,name="delete_item"),
]
