from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_list, name='reservation_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create/<int:event_id>/', views.reservation_create, name='reservation_create'),
    path('<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('<int:pk>/update/', views.reservation_update, name='reservation_update'),
    path('<int:pk>/cancel/', views.reservation_cancel, name='reservation_cancel'),
    path('<int:pk>/resend-email/', views.resend_confirmation_email, name='resend_confirmation_email'),
]
