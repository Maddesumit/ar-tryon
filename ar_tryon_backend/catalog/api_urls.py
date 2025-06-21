"""
API URL configuration for catalog app.
This file defines REST API endpoints for product catalog functionality.
"""

from django.urls import path
from . import api_views

app_name = 'catalog_api'

urlpatterns = [
    # Product API endpoints
    path('products/', api_views.ProductListAPIView.as_view(), name='product_list_api'),
    path('products/<slug:slug>/', api_views.ProductDetailAPIView.as_view(), name='product_detail_api'),
    
    # Category API endpoints
    path('categories/', api_views.CategoryListAPIView.as_view(), name='category_list_api'),
    
    # Brand API endpoints
    path('brands/', api_views.BrandListAPIView.as_view(), name='brand_list_api'),
    
    # Statistics endpoint
    path('stats/', api_views.catalog_stats, name='catalog_stats'),
]
