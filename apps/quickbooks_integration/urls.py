from django.urls import path
from apps.quickbooks_integration.views import *

urlpatterns = [
    path('login/', quickbooks_login, name='quickbooks_login'),
    path('callback/', quickbooks_callback, name='quickbooks_callback'),
    path('dashboard/', quickbooks_dashboard, name='quickbooks_dashboard'),
    path('refresh_token/', refresh_token, name='quickbooks_refresh_token'),
    path('customer_create/', customer_create, name='customer_create'),
    path('fetch_customers/', fetch_customers, name='fetch_customers'),
]