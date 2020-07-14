from django.urls import path,re_path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('pending_redeem/',views.pending_redeem,name='pending_redeem')
]