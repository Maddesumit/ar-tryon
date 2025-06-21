"""
API views for catalog app using Django REST Framework
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from .models import Product, Category, Brand
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer


class ProductListAPIView(generics.ListAPIView):
    """
    API endpoint for listing products with filtering and search
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Allow public access
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search)
            )
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Brand filter
        brand = self.request.query_params.get('brand', None)
        if brand:
            queryset = queryset.filter(brand__slug=brand)
        
        # Gender filter
        gender = self.request.query_params.get('gender', None)
        if gender:
            queryset = queryset.filter(gender=gender)
        
        # Price range filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Featured filter
        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Sorting
        sort = self.request.query_params.get('sort', 'name')
        if sort == 'price_low':
            queryset = queryset.order_by('price')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'popular':
            queryset = queryset.order_by('-view_count')
        else:
            queryset = queryset.order_by('name')
        
        # Limit results (moved after sorting)
        limit = self.request.query_params.get('limit', None)
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass
        
        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a single product
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]  # Allow public access
    lookup_field = 'slug'


class CategoryListAPIView(generics.ListAPIView):
    """
    API endpoint for listing categories
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Allow public access


class BrandListAPIView(generics.ListAPIView):
    """
    API endpoint for listing brands
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]  # Allow public access


@api_view(['GET'])
@permission_classes([AllowAny])
def catalog_stats(request):
    """
    API endpoint for catalog statistics
    """
    stats = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_brands': Brand.objects.filter(is_active=True).count(),
        'featured_products': Product.objects.filter(is_active=True, is_featured=True).count(),
        'ar_enabled_products': Product.objects.filter(is_active=True, ar_enabled=True).count(),
    }
    return Response(stats)
