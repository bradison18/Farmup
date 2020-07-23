
"""today URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import include,path
from . import views
app_name = "farmerandlandlord"

urlpatterns = [
    #path('admin/', admin.site.urls),
    url('^$',views.farmersearch,name='farmersearch'),
    url('^filterfarmer/',views.filterfarmer,name='filterfarmer'),
    url('^landlordsearch/',views.landlordsearch),
    path('dashboardlandlord/',views.dashboardlandlord,name='dashboardlandlord'),
    path('dashboardfarmer/',views.dashboardfarmer,name='dashboardfarmer'),
    url('^formaddland/',views.formaddland,name='formaddland'),
    url('^addland/',views.addland,name='addland'),
    path('formeditland/<str:land_id>/',views.formeditland,name='formeditland'),
    path('editland/<str:land_id>/',views.editland,name='editland'),
    path('acceptrequest/<str:land_id>/<str:user_id>/<str:username>/',views.acceptrequest,name='acceptrequest'),
    url('^landlordviewrequest/',views.landlordviewrequest,name='landlordviewrequest'),
    path('infoland/<str:land_id>/',views.infoland,name='infoland'),
    path('leaveland/<str:lwg>/',views.leaveland,name='leaveland'),
    path('deleteland/<str:land_id>/',views.deleteland,name='deleteland'),
    path('farmerrequest/<str:land_id>/<str:user_id>/',views.farmerrequest,name='farmerrequest'),
]
