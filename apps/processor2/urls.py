from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.processor2 import views

urlpatterns = [
    path('list_processor2/', views.list_processor2, name='list_processor2'),
    path('add_processor2/', views.add_processor2, name='add_processor2'),
    path('add_processor2_user/<int:pk>/', views.add_processor2_user, name='add_processor2_user'),
    path('processor2_update/<int:pk>/', views.processor2_update, name='processor2_update'),
    path('processor2_change_password/<int:pk>/', views.processor2_change_password, name='processor2_change_password'),
    path('processor2_delete/<int:pk>/', views.processor2_delete, name='processor2_delete'),
    path('add_bale_processor2/', views.add_bale_processor2, name='add_bale_processor2'),
    path('list_bale_processor2/', views.list_bale_processor2, name='list_bale_processor2'),
    path('classing_csv_list_view2/<int:pk>', views.classing_csv_list_view2, name='classing_csv_list_view2'),
    path('processor2_classing_csv_all2/', views.processor2_classing_csv_all2, name='processor2_classing_csv_all2'),
    # 19-05-23 t2_classing_ewr_report_list
    path('t2_classing_ewr_report_list/', views.t2_classing_ewr_report_list, name='t2_classing_ewr_report_list'),
    path('t2_classing_ewr_report_all_downlaod/<str:p2_id>/<str:level>', views.t2_classing_ewr_report_all_downlaod, name='t2_classing_ewr_report_all_downlaod'),
   
    path('addlocation_processor2/', views.addlocation_processor2, name="addlocation_processor2"),
    path('location_list_processor2/', views.location_list_processor2, name="location_list_processor2"),
    path('location_edit_processor2/<int:pk>/', views.location_edit_processor2, name="location_edit_processor2"),
    path('location_delete_processor2/<int:pk>/', views.location_delete_processor2, name="location_delete_processor2"),


    # path('load_subcategories/', views.load_subcategories, name="load_subcategories"),
    path('add_outbound_shipment_processor2/', views.add_outbound_shipment_processor2, name="add_outbound_shipment_processor2"),
    path('outbound_shipment_list/', views.outbound_shipment_list, name="outbound_shipment_list"),
    path('inbound_shipment_list/', views.inbound_shipment_list, name="inbound_shipment_list"),
    path('inbound_shipment_view/<int:pk>/', views.inbound_shipment_view, name="inbound_shipment_view"),
    path('inbound_shipment_edit/<int:pk>/', views.inbound_shipment_edit, name="inbound_shipment_edit"),
    
    path('recive_shipment/', views.recive_shipment, name="recive_shipment"),
    path('link_processor_two/', views.link_processor_two, name="link_processor_two"),
    path('processor2_processor_management/', views.processor2_processor_management, name="processor2_processor_management"),
]