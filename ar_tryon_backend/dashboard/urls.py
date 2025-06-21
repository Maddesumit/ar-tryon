"""
URL patterns for the custom admin dashboard.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_overview, name='overview'),
    path('products/', views.product_management, name='product_management'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:product_id>/', views.product_delete, name='product_delete'),
    path('products/bulk-actions/', views.bulk_product_actions, name='bulk_product_actions'),
    path('images/', views.image_management, name='image_management'),
    path('api/analytics/', views.analytics_api, name='analytics_api'),
]
