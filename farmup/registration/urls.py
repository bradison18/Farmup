
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
    path('save_password/',views.save_password,name='save_password'),
    path('my_profile/',views.display_profile,name='my_profile'),
    path('edit_profile_display',views.display_edit_profile,name='display_edit_profile'),
    path('edit_profile',views.edit_profile,name="edit_profile"),
    path('verify_lands',views.verify_lands,name="verify_lands"),
    url(r'accept_land/(?P<id>[0-9]+)/',views.accept_land,name="accept_land"),
    url(r'reject_land/(?P<id>[0-9]+)/',views.reject_land,name="reject_land")
    ]
