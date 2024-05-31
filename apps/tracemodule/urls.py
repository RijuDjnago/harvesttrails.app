from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.tracemodule import views

urlpatterns = [
    path('traceability_report_list/', views.traceability_report_list, name='traceability_report_list'),
    path('showsustainability_metrics/<str:get_search_by>/<int:field_id>/', views.showsustainability_metrics, name='showsustainability_metrics'),
    path('showquality_metrics/<str:get_search_by>/<str:delivery_idd>/', views.showquality_metrics, name='showquality_metrics'),
    
    path('traceability_report_Origin_csv_download/<str:select_crop>/<str:get_search_by>/<str:search_text>/<str:from_date>/<str:to_date>/', views.traceability_report_Origin_csv_download, name='traceability_report_Origin_csv_download'),
    path('traceability_report_WIP1_csv_download/<str:select_crop>/<str:get_search_by>/<str:search_text>/<str:from_date>/<str:to_date>/', views.traceability_report_WIP1_csv_download, name='traceability_report_WIP1_csv_download'),
    path('traceability_report_T1_Processor_csv_download/<str:select_crop>/<str:get_search_by>/<str:search_text>/<str:from_date>/<str:to_date>/', views.traceability_report_T1_Processor_csv_download, name='traceability_report_T1_Processor_csv_download'),
    path('traceability_report_WIP2_csv_download/<str:select_crop>/<str:get_search_by>/<str:search_text>/<str:from_date>/<str:to_date>/', views.traceability_report_WIP2_csv_download, name='traceability_report_WIP2_csv_download'),
    path('traceability_report_T2_Processor_csv_download/<str:select_crop>/<str:get_search_by>/<str:search_text>/<str:from_date>/<str:to_date>/', views.traceability_report_T2_Processor_csv_download, name='traceability_report_T2_Processor_csv_download'),
    # all csv download
    path('traceability_report_all_csv_download/<str:select_crop>/<str:get_search_by>/<str:search_text>/<str:from_date>/<str:to_date>/', views.traceability_report_all_csv_download, name='traceability_report_all_csv_download'),
    # autocomplete suggestions 03-04-23
    path('autocomplete_suggestions/<str:select_search>/<str:select_crop_id>/', views.autocomplete_suggestions, name='autocomplete_suggestions'),

    path('display_traceability_report/', views.display_traceability_report, name="display_traceability_report"),
    path('test_map/', views.test_map, name='test_map'),
]