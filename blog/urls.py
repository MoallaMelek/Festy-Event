from django.urls import path
from . import views

urlpatterns = [
    # Blog
    path('', views.blog_list, name='blog_list'),
    path('category/<slug:slug>/', views.blog_category, name='blog_category'),
    path('post/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_blog_comment'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
