
from django.conf.urls import url
from django.urls import path,include
from . import views
from django.conf.urls import url
app_name = "registration"

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/',views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('login_display/',views.login_display,name='login_display'),
    path('register_display/',views.register_display,name='register_display'),
    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',views.activate, name='activate'),
    url(r'verify_reset_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',views.verify_reset_password, name='verify_reset_password'),
    path('reset_display/',views.reset_display,name='reset_display'),
    path('reset_password/',views.reset_password,name='reset_password'),
    path('save_password/',views.save_password,name='save_password')
    ]
