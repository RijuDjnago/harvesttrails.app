from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.processor4 import views


urlpatterns = [
    path('inbound_shipment_list_processor4/', views.inbound_shipment_list, name="inbound_shipment_list4"),
    path('inbound_shipment_view_processor4/<int:pk>/', views.inbound_shipment_view, name="inbound_shipment_view4"),
    path('inbound_shipment_edit_processor4/<int:pk>/', views.inbound_shipment_edit, name="inbound_shipment_edit4"),
    path('receive_shipment_processor4/', views.receive_shipment, name="receive_shipment4"),
    path('rejected_shipments_csv_download_f4/', views.rejected_shipments_csv_download_for_t4, name="rejected_shipments_csv_download_f4"),
    path('all_shipments_csv_download_t4/', views.all_shipments_csv_download_for_t4, name="all_shipments_csv_download_t4"),
]
