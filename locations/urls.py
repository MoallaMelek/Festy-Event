from django.urls import path
from . import views

urlpatterns = [
    path('locations/', views.location_list, name='location_list'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/map/', views.tunisia_map, name='tunisia_map'),
    path('locations/<int:pk>/', views.location_detail, name='location_detail'),
    path('locations/<int:pk>/edit/', views.location_update, name='location_update'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),
    path('locations/<int:pk>/calendar/', views.location_calendar, name='location_calendar'),
    path('locations/availability/', views.locations_availability, name='locations_availability'),
]
