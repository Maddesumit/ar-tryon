"""
Views for catalog app.
This app handles product catalog and browsing functionality.
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from .models import Category, Brand, Product, ProductReview

def catalog_home(request):
    """
    Catalog home page with featured products and categories.
    """
    # Get featured products
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_available=True
    ).select_related('brand', 'category')[:8]
    
    # Get active categories with product counts
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        product_count=Count('products', filter=Q(products__is_available=True))
    ).order_by('sort_order', 'name')
    
    # Get statistics for JSON response
    stats = {
        'total_products': Product.objects.filter(is_available=True).count(),
        'total_categories': categories.count(),
        'total_brands': Brand.objects.filter(is_active=True).count(),
        'featured_products': featured_products.count(),
    }
    
    # If this is an API request, return JSON
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'message': 'Hello from Catalog app!',
            'app': 'catalog',
            'description': 'This app handles product catalog and inventory',
            'stats': stats
        })
    
    # Otherwise render HTML template
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'stats': stats,
    }
    return render(request, 'catalog/home.html', context)

def product_list(request):
    """
    Product listing page with filtering and pagination.
    """
    # Get base queryset
    products = Product.objects.filter(is_available=True).select_related('brand', 'category')
    
    # Apply filters
    category_slug = request.GET.get('category')
    brand_slug = request.GET.get('brand')
    search_query = request.GET.get('search')
    gender = request.GET.get('gender')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    if gender:
        products = products.filter(gender=gender)
    
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass
    
    # Sorting
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.annotate(review_count=Count('reviews')).order_by('-review_count')
    else:  # default to name
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for sidebar
    categories = Category.objects.filter(is_active=True).order_by('name')
    brands = Brand.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'brands': brands,
        'current_filters': {
            'category': category_slug,
            'brand': brand_slug,
            'search': search_query,
            'gender': gender,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort_by,
        }
    }
    
    return render(request, 'catalog/product_list.html', context)

def product_detail(request, slug):
    """
    Product detail page with reviews and try-on options.
    """
    # Get product with related data
    product = get_object_or_404(
        Product.objects.select_related('brand', 'category').prefetch_related('images'),
        slug=slug,
        is_available=True
    )
    
    # Get product reviews
    reviews = ProductReview.objects.filter(
        product=product,
        is_approved=True
    ).select_related('user').order_by('-created_at')
    
    # Calculate review statistics
    review_stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Get related products (same category, different product)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id).select_related('brand')[:4]
    
    context = {
        'product': product,
        'reviews': reviews[:10],  # Show first 10 reviews
        'review_stats': review_stats,
        'related_products': related_products,
        'available_sizes': product.get_available_sizes_list(),
        'available_colors': product.get_available_colors_list(),
    }
    
    return render(request, 'catalog/product_detail.html', context)

def category_list(request):
    """
    List all categories with product counts.
    """
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        product_count=Count('products', filter=Q(products__is_available=True))
    ).order_by('sort_order', 'name')
    
    # If this is an API request, return JSON
    if request.headers.get('Accept') == 'application/json':
        categories_data = [
            {
                'name': cat.name,
                'slug': cat.slug,
                'description': cat.description,
                'product_count': cat.product_count,
                'image_url': cat.image.url if cat.image else None,
            }
            for cat in categories
        ]
        return JsonResponse({'categories': categories_data})
    
    return render(request, 'catalog/category_list.html', {'categories': categories})

def brand_detail(request, slug):
    """
    Brand detail page with their products.
    """
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    
    # Get brand products
    products = Product.objects.filter(
        brand=brand,
        is_available=True
    ).select_related('category').order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'brand': brand,
        'page_obj': page_obj,
        'products': page_obj.object_list,
    }
    
    return render(request, 'catalog/brand_detail.html', context)

def category_detail(request, slug):
    """
    Category detail page with products in that category.
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # Get category products
    products = Product.objects.filter(
        category=category,
        is_available=True
    ).select_related('brand').order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'products': page_obj.object_list,
    }
    
    return render(request, 'catalog/category_detail.html', context)
