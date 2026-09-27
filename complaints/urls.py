from django.urls import path
from . import views

urlpatterns = [
    # URLs Utilisateur
    path('', views.complaint_list, name='complaint_list'),
    path('create/', views.complaint_create, name='complaint_create'),
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
    
    # URLs Admin
    path('admin/list/', views.admin_complaint_list, name='admin_complaint_list'),
    path('admin/<int:pk>/respond/', views.admin_complaint_respond, name='admin_complaint_respond'),
]
