from django.urls import path
from . import views

urlpatterns = [
    path('contracts/', views.contract_list, name='contract_list'),
    path('contracts/create/', views.contract_create, name='contract_create'),
    path('contracts/<int:pk>/', views.contract_detail, name='contract_detail'),
    path('contracts/<int:pk>/edit/', views.contract_update, name='contract_update'),
    path('contracts/<int:pk>/activate/', views.contract_activate, name='contract_activate'),
    path('contracts/<int:pk>/complete/', views.contract_complete, name='contract_complete'),
    path('contracts/<int:pk>/cancel/', views.contract_cancel, name='contract_cancel'),
    path('contracts/<int:pk>/sign/', views.contract_sign, name='contract_sign'),
    path('contracts/<int:pk>/admin-sign/', views.contract_admin_sign, name='contract_admin_sign'),
]
