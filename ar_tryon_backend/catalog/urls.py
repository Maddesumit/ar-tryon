"""
URL configuration for catalog app.
This file defines all the URL patterns for product catalog functionality.
"""

from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Main catalog pages
    path('', views.catalog_home, name='catalog_home'),
    path('products/', views.product_list, name='product_list'),
    path('categories/', views.category_list, name='category_list'),
    
    # Detail pages
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
]
