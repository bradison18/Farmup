
from django.conf.urls import url
from django.urls import path,include
from . import views
app_name = "registration"

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),

    ]
