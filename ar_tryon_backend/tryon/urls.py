"""
URL configuration for tryon app.
This file defines all the URL patterns for virtual try-on functionality.
"""

from django.urls import path
from . import views

app_name = 'tryon'

urlpatterns = [
    # Basic hello world view to test the app is working
    path('', views.tryon_home, name='tryon_home'),
    
    # Try-on URLs (we'll add these in later phases)
    path('upload/', views.upload_image, name='upload_image'),
    path('results/', views.tryon_results, name='tryon_results'),
]
