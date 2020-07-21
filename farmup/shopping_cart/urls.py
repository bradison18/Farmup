
from django.conf.urls import url
from django.urls import path,include
from . import views

app_name = "shopping_cart"


urlpatterns = [
    path('buyingportal/', views.buyingpage, name='buyingpage'),
    path('addCropElements/', views.addCropElements, name='addCropElements'),
    path('', views.addCropElements, name="add_to_cart"),
    path('buyingportal/cart/',views.checkout,name="cart"),
    path('deleteitems/<item_name>',views.delete_from_cart,name="delete_item"),
    path('add',views.add),
    path('buyingportal/checkout/',views.checkout_sub,name='checkout'),
    path('buyingportal/tempcheck/',views.add_items,name='temp'),
    path('search',views.search,name='search'),
    path('increase_quan/<cropname>/<quan>/<oper>',views.change_quantity,name='increase'),
    path('decrease_quan/<cropname>/<quan>',views.decrease_quantity,name='decrease')
    # path('verify_sms/',views.)
]
