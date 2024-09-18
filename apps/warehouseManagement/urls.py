from django.urls import path
from .views import *


urlpatterns = [
    path('add-distributor/', add_distributor, name='add-distributor'),
    path('add-distributor-user/<int:pk>/', add_distributor_user, name='add-distributor-user'),
    path('list-distributor/', distributor_list, name='list-distributor'),
    path('update-distributor/<int:pk>/', distributor_update, name='update-distributor'),
    path('distributor-change-password/<int:pk>/', distributor_change_password, name='distributor-change-password'),
    path('add-warehouse/', add_warehouse, name='add-warehouse'),
    path('list-warehouse/', list_warehouse, name='list-warehouse'),
    path('update-warehouse/<int:pk>/', warehouse_update, name='update-warehouse'),
    path('warehouse-change-password/<int:pk>/', warehouse_change_password, name='warehouse-change-password'),
    path('add-customer/', add_customer, name='add-customer'),
    path('list-customer/', list_customer, name='list-customer'),
    path('update-customer/<int:pk>/', customer_update, name='update-customer'),
    path('customer-change-password/<int:pk>/', customer_change_password, name='customer-change-password'),
    path('customer_upload_documents/<int:pk>/', customer_upload_documents,name='customer_upload_documents' ),
    path('customer_view/<int:pk>/', customer_view, name='customer_view'),
    path('add-processor-shipment/', create_processor_shipment, name='add-processor-shipment'),
    path('list-processor-shipment/', list_processor_shipment, name='list-processor-shipment'),
    path('view-processor-shipment/<int:pk>/', processor_shipment_view, name='view-processor-shipment'),
    path('edit-processor-shipment/<int:pk>/', edit_processor_shipment, name='edit-processor-shipment'),

    path('add-warehouse-shipment/', create_warehouse_shipment, name='add-warehouse-shipment'),
    path('list-warehouse-shipment/', warehouse_shipment_list, name='list-warehouse-shipment'),
    path('warehouse-shipment-view/<int:pk>/', warehouse_shipment_view, name='warehouse-shipment-view'),
    path('edit-warehouse-shipment/<int:pk>/', edit_warehouse_shipment, name='edit-warehouse-shipment'),
    path('warehouse-shipment-invoice/<int:pk>/', warehouse_shipment_invoice, name='warehouse-shipment-invoice'),
    path('create-payment/<int:pk>/<str:type>/', create_payment_for_shipment, name='create_payment_for_shipment'),
    path('checkout-success/<int:pk>/<str:type>/<str:checkout_session_id>/', checkout_success, name='checkout-success'),
    path('generate_invoice/<int:pk>/', generate_invoice, name='generate_invoice'),   
    path('processor_shipment_generate_report/', processor_shipment_generate_report, name='processor_shipment_generate_report'),
    path('processor_shipment_export_csv/', processor_shipment_export_csv, name='processor_shipment_export_csv'),
    path('export_csv_for_single_shipment_processor/<str:shipment_id>', processor_shipment_csv_single_shipment, name='export_csv_for_single_shipment_processor'),
    path('warehouse_shipment_generate_report/', warehouse_shipment_generate_report, name='warehouse_shipment_generate_report'),
    path('warehouse_shipment_export_csv/', warehouse_shipment_export_csv, name='warehouse_shipment_export_csv'),
    path('export_csv_for_single_shipment_warehouse/<str:shipment_id>', warehouse_shipment_csv_single_shipment, name='export_csv_for_single_shipment_warehouse'),
    
]
