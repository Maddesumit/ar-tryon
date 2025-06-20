"""
Views for catalog app.
This app handles product catalog functionality.
"""

from django.shortcuts import render
from django.http import JsonResponse

def catalog_home(request):
    """
    A simple view that returns a JSON response.
    This is our 'Hello World' view for the catalog app.
    """
    return JsonResponse({
        'message': 'Hello from Catalog app!',
        'app': 'catalog',
        'description': 'This app handles product catalog and inventory'
    })

# Placeholder views for Phase 3
def product_list(request):
    """Product list view - to be implemented in Phase 3"""
    return JsonResponse({'message': 'Product list - coming in Phase 3!'})

def product_detail(request, product_id):
    """Product detail view - to be implemented in Phase 3"""
    return JsonResponse({'message': f'Product {product_id} details - coming in Phase 3!'})

def category_list(request):
    """Category list view - to be implemented in Phase 3"""
    return JsonResponse({'message': 'Category list - coming in Phase 3!'})
