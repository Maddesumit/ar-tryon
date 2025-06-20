"""
URL configuration for users app.
This file defines all the URL patterns (routes) for user-related functionality.
"""

from django.urls import path
from . import views

# The app_name helps Django identify these URLs when we use reverse() or {% url %} tags
app_name = 'users'

urlpatterns = [
    # Basic hello world view to test the app is working
    path('', views.user_home, name='user_home'),
    
    # Authentication URLs (we'll add these in Phase 2)
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
