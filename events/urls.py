from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.event_create, name='event_create'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/edit/', views.event_update, name='event_update'),
    path('<int:pk>/confirm/', views.event_confirm, name='event_confirm'),
    path('<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Recommandations utilisateurs
    path('<int:event_id>/recommendations/', views.recommendation_list, name='recommendation_list'),
    path('<int:event_id>/recommend/', views.recommendation_create, name='recommendation_create'),
    path('recommendation/<int:pk>/edit/', views.recommendation_update, name='recommendation_update'),
    path('recommendation/<int:pk>/delete/', views.recommendation_delete, name='recommendation_delete'),
    path('recommendation/<int:pk>/helpful/', views.recommendation_helpful, name='recommendation_helpful'),
    
    # Admin - Gestion des recommandations
    path('admin/recommendations/', views.admin_recommendation_list, name='admin_recommendation_list'),
    path('admin/recommendations/<int:pk>/', views.admin_recommendation_detail, name='admin_recommendation_detail'),
    path('admin/recommendations/<int:pk>/approve/', views.admin_recommendation_approve, name='admin_recommendation_approve'),
    path('admin/recommendations/<int:pk>/feature/', views.admin_recommendation_feature, name='admin_recommendation_feature'),
    path('admin/recommendations/<int:pk>/respond/', views.admin_recommendation_respond, name='admin_recommendation_respond'),
    path('admin/recommendations/<int:pk>/delete/', views.admin_recommendation_delete, name='admin_recommendation_delete'),
]
