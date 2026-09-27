"""
URL configuration for festy_event project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/events/', permanent=False)),
    path('events/', include('events.urls')),
    path('reservations/', include('reservations.urls')),
    path('users/', include('users.urls')),
    path('complaints/', include('complaints.urls')),
    path('', include('payments.urls')),
    path('', include('locations.urls')),
    path('', include('contracts.urls')),
    path('blog/', include('blog.urls')),
    path('reviews/', include('reviews.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
