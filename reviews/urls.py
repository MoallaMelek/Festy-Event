from django.urls import path
from . import views

urlpatterns = [
    # Reviews
    path('add/<int:content_type_id>/<int:object_id>/', views.add_review, name='add_review'),
    path('<int:pk>/helpful/', views.mark_helpful, name='mark_review_helpful'),
    
    # FAQ
    path('faq/', views.faq_list, name='faq_list'),
    path('faq/<int:pk>/helpful/', views.faq_helpful, name='faq_helpful'),
    
    # Contact
    path('contact/', views.contact, name='contact'),
]
