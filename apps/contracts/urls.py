from django.urls import path

from apps.contracts import views



urlpatterns = [
    path('list/', views.ContractsListView.as_view(), name='contract-list'),
    path('<int:pk>/pdf/', views.ContractPdfView.as_view(), name='contract-pdf'),
    path('add/', views.ContractsCreateView.as_view(), name='contract-add'),
    path('signed-contracts/', views.SignedContractsListView.as_view(), name='signed-contract-list'),
    path('sign-contracts/', views.ContractsSignSaveView.as_view(), name='sign-contract-details'),
    path('<int:pk>/detail/', views.ContractDetailView.as_view(), name='contract-details'),
    path('<int:pk>/update/', views.ContractsUpdateView.as_view(), name='contract-update'),
    path('signed/<int:pk>/details/', views.SignedContractDetailView.as_view(), name='signed-contract-details'),
    path('signed/verification/save', views.ContractsSignVerificationSaveView.as_view(), name='signed-contract-details-save'),
    path('<int:contract_id>/grower/<int:grower_id>', views.UpdateDocumentSignedView.as_view(), name='docusign-contract-submit'),
    path('docusign/login', views.DocusignCallbackUrlForAuth.as_view(),
         name='docusign-login'),
]