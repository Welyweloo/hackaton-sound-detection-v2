"""sounddetection URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from core import views

app_name = 'core'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('get_assistant_status/<int:serial_number>/', views.get_assistant_status, name='get_assistant_status'),
    path('get_listenning_status/', views.get_listenning_status, name='get_listenning_status'),
    path('set_listenning_status/<int:serial_number>/', views.set_listenning_status, name='set_listenning_status'),
    path('set_sound_detected/', views.set_sound_detected, name='set_sound_detected'),
    path('get_sound_detected/', views.get_sound_detected, name='get_sound_detected'),
    path('confirm_alert/<int:detection_id>/', views.confirm_alert, name='confirm_alert'),
    path('cancel_alert/', views.cancel_alert, name='cancel_alert'),
    path('dashboard', views.dashboard, name='dashboard'),
]
