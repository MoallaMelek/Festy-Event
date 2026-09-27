from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    # Admin user management
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/update/', views.admin_user_update, name='admin_user_update'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/users/<int:user_id>/toggle/', views.admin_user_toggle_status, name='admin_user_toggle_status'),
]
