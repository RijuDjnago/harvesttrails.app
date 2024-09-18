from django.urls import path
from apps.quickbooks_integration.views import *

urlpatterns = [
    path('connect/', quickbooks_connect, name='quickbooks_connect'),
    path('callback/', quickbooks_callback, name='quickbooks_callback'),
]