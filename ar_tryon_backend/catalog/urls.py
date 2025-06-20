"""
URL configuration for catalog app.
This file defines all the URL patterns for product catalog functionality.
"""

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Basic hello world view to test the app is working
    path('', views.catalog_home, name='catalog_home'),
    
    # Product URLs (we'll add these in Phase 3)
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('categories/', views.category_list, name='category_list'),
]
