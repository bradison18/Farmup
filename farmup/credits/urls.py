from django.urls import path,re_path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('pending_redeem/',views.pending_redeem,name='pending_redeem'),
    path('verify_sms/',views.verify_sms,name='verify_sms'),
    path('add_balance/',views.add_balance,name='add_balance'),
    # path('', views.HomePageView.as_view(), name='home'),
    path('home/',views.home,name='credits_home'),
    path('config/', views.stripe_config),
    path('create-checkout-session/', views.create_checkout_session),
    path('success/<session_id>/<trans_id>', views.success),
    path('cancelled/<session_id>/<trans_id>', views.cancel),
    path('transactions/',views.transactions,name='transactions')

]