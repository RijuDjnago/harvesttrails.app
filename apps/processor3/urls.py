from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.processor3 import views

urlpatterns = [
    path('list_processor3/', views.processor3_list, name='list_processor3'),
    path('add_processor3/', views.add_processor3, name='add_processor3'),
    path('update_processor3/<int:pk>/', views.processor3_update, name='update_processor3'),
    path('p3_change_password/<int:pk>/', views.processor3_change_password, name='change_password'),
    path('processor3_delete/<int:pk>/', views.processor3_delete, name='processor3_delete'),
    path('add_p3_user/<int:pk>/', views.add_processor3_user, name='add_p3_user'),
    path('test/', views.check_riju, name='test'),


    path('inbound_shipment_list/', views.inbound_shipment_list, name="inbound_shipment_list"),
    path('inbound_shipment_view/<int:pk>/', views.inbound_shipment_view, name="inbound_shipment_view"),
    path('inbound_shipment_edit/<int:pk>/', views.inbound_shipment_edit, name="inbound_shipment_edit"),
    path('receive_shipment/', views.receive_shipment, name="receive_shipment"),
    path('add_outbound_shipment_processor3/', views.add_outbound_shipment_processor3, name="add_outbound_shipment_processor3"),
    path('outbound_shipment_list_processor3/', views.outbound_shipment_list_processor3, name="outbound_shipment_list_processor3"),
    
]