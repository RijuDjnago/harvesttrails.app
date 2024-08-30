from django.urls import path
from .views import *


urlpatterns = [
    path('add-distributor/', add_distributor, name='add-distributor'),
    # path('add-distributor-user/', add_distributor_user, name='add-distributor-user'),
    path('list-distributor/', distributor_list, name='list-distributor'),
    path('add-warehouse/', add_warehouse, name='add-warehouse'),
    path('list-warehouse/', list_warehouse, name='list-warehouse'),
    path('add-customer/', add_customer, name='add-customer'),
    path('list-customer/', list_customer, name='list-customer'),
    
    path('add-processor-shipment/', create_processor_shipment, name='add-processor-shipment'),
    path('list-processor-shipment/', list_processor_shipment, name='list-processor-shipment'),
    
]
