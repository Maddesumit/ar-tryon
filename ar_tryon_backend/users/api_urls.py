"""
API URL configuration for users app.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import api_views

app_name = 'users_api'

urlpatterns = [
    # Authentication endpoints
    path('register/', api_views.register_user, name='register'),
    path('login/', api_views.login_user, name='login'),
    path('logout/', api_views.logout_user, name='logout'),
    
    # JWT token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User profile endpoints
    path('profile/', api_views.UserProfileView.as_view(), name='user_profile'),
    path('details/', api_views.UserDetailView.as_view(), name='user_details'),
    path('dashboard/', api_views.user_dashboard, name='user_dashboard'),
    
    # Password management
    path('change-password/', api_views.change_password, name='change_password'),
]
