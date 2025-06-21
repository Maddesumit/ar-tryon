"""
Custom admin dashboard views for AR Try-On admin interface.
Provides additional functionality beyond Django's default admin.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json

from catalog.models import Product, Category, Brand, ProductImage, ProductReview
from users.models import User


@staff_member_required
def dashboard_overview(request):
    """
    Main dashboard overview page with statistics and charts.
    """
    # Calculate key statistics
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_available=True).count()
    products_with_images = Product.objects.filter(images__isnull=False).distinct().count()
    products_with_tryon = Product.objects.filter(is_try_on_enabled=True).count()
    
    # Category statistics
    categories = Category.objects.annotate(
        product_count=Count('products'),
        active_products=Count('products', filter=Q(products__is_available=True))
    ).order_by('-product_count')
    
    # Brand statistics
    brands = Brand.objects.annotate(
        product_count=Count('products'),
        active_products=Count('products', filter=Q(products__is_available=True))
    ).order_by('-product_count')
    
    # Recent products (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_products = Product.objects.filter(created_at__gte=week_ago).order_by('-created_at')
    
    # Products needing attention
    products_without_images = Product.objects.filter(images__isnull=True)
    low_stock_products = Product.objects.filter(stock_quantity__lt=10, stock_quantity__gt=0)
    out_of_stock_products = Product.objects.filter(stock_quantity=0)
    
    # Review statistics
    total_reviews = ProductReview.objects.count()
    pending_reviews = ProductReview.objects.filter(is_approved=False).count()
    avg_rating = ProductReview.objects.filter(is_approved=True).aggregate(
        avg_rating=Avg('rating')
    )['avg_rating'] or 0
    
    context = {
        'stats': {
            'total_products': total_products,
            'active_products': active_products,
            'products_with_images': products_with_images,
            'products_with_tryon': products_with_tryon,
            'total_reviews': total_reviews,
            'pending_reviews': pending_reviews,
            'avg_rating': round(avg_rating, 1),
        },
        'categories': categories[:10],  # Top 10 categories
        'brands': brands[:10],  # Top 10 brands
        'recent_products': recent_products[:5],
        'products_without_images': products_without_images[:5],
        'low_stock_products': low_stock_products[:5],
        'out_of_stock_products': out_of_stock_products[:5],
    }
    
    return render(request, 'dashboard/overview.html', context)


@staff_member_required
def product_management(request):
    """
    Enhanced product management page with bulk operations.
    """
    products = Product.objects.select_related('category', 'brand').prefetch_related('images')
    
    # Apply filters
    category_filter = request.GET.get('category')
    brand_filter = request.GET.get('brand')
    status_filter = request.GET.get('status')
    search = request.GET.get('search')
    
    if category_filter:
        products = products.filter(category__slug=category_filter)
    if brand_filter:
        products = products.filter(brand__slug=brand_filter)
    if status_filter == 'active':
        products = products.filter(is_available=True)
    elif status_filter == 'inactive':
        products = products.filter(is_available=False)
    elif status_filter == 'no_images':
        products = products.filter(images__isnull=True)
    elif status_filter == 'low_stock':
        products = products.filter(stock_quantity__lt=10, stock_quantity__gt=0)
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) |
            Q(brand__name__icontains=search)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'current_filters': {
            'category': category_filter,
            'brand': brand_filter,
            'status': status_filter,
            'search': search,
        }
    }
    
    return render(request, 'dashboard/product_management.html', context)


@staff_member_required
def bulk_product_actions(request):
    """
    Handle bulk actions on products.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            messages.error(request, 'No products selected.')
            return redirect('dashboard:product_management')
        
        products = Product.objects.filter(id__in=product_ids)
        count = products.count()
        
        if action == 'activate':
            products.update(is_available=True)
            messages.success(request, f'{count} products activated.')
        elif action == 'deactivate':
            products.update(is_available=False)
            messages.success(request, f'{count} products deactivated.')
        elif action == 'enable_tryon':
            products.update(is_try_on_enabled=True)
            messages.success(request, f'{count} products enabled for try-on.')
        elif action == 'disable_tryon':
            products.update(is_try_on_enabled=False)
            messages.success(request, f'{count} products disabled for try-on.')
        elif action == 'mark_featured':
            products.update(is_featured=True)
            messages.success(request, f'{count} products marked as featured.')
        elif action == 'unmark_featured':
            products.update(is_featured=False)
            messages.success(request, f'{count} products unmarked as featured.')
        else:
            messages.error(request, 'Invalid action.')
    
    return redirect('dashboard:product_management')


@staff_member_required
def image_management(request):
    """
    Manage product images with bulk upload capabilities.
    """
    products_without_images = Product.objects.filter(images__isnull=True)
    products_with_few_images = Product.objects.annotate(
        image_count=Count('images')
    ).filter(image_count__lt=3)
    
    context = {
        'products_without_images': products_without_images,
        'products_with_few_images': products_with_few_images,
    }
    
    return render(request, 'dashboard/image_management.html', context)


@staff_member_required
def analytics_api(request):
    """
    API endpoint for dashboard analytics data.
    """
    # Category distribution
    category_data = Category.objects.annotate(
        count=Count('products')
    ).values('name', 'count')
    
    # Products by month (last 12 months)
    from django.db.models.functions import TruncMonth
    monthly_data = Product.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Stock status distribution
    stock_data = [
        {'status': 'In Stock', 'count': Product.objects.filter(stock_quantity__gt=10).count()},
        {'status': 'Low Stock', 'count': Product.objects.filter(stock_quantity__lte=10, stock_quantity__gt=0).count()},
        {'status': 'Out of Stock', 'count': Product.objects.filter(stock_quantity=0).count()},
    ]
    
    return JsonResponse({
        'categories': list(category_data),
        'monthly_products': list(monthly_data),
        'stock_status': stock_data,
    })


@staff_member_required
def product_add(request):
    """
    Add a new product.
    """
    if request.method == 'POST':
        # Handle form submission
        form_data = request.POST
        files = request.FILES
        
        try:
            # Create new product
            product = Product.objects.create(
                name=form_data.get('name'),
                slug=form_data.get('slug') or form_data.get('name').lower().replace(' ', '-'),
                description=form_data.get('description', ''),
                short_description=form_data.get('short_description', ''),
                category_id=form_data.get('category'),
                brand_id=form_data.get('brand'),
                price=float(form_data.get('price', 0)),
                sale_price=float(form_data.get('sale_price', 0)) if form_data.get('sale_price') else None,
                stock_quantity=int(form_data.get('stock_quantity', 0)),
                available_sizes=form_data.get('available_sizes', ''),
                available_colors=form_data.get('available_colors', ''),
                gender=form_data.get('gender', 'U'),
                is_available=form_data.get('is_available') == 'on',
                is_featured=form_data.get('is_featured') == 'on',
                is_try_on_enabled=form_data.get('is_try_on_enabled') == 'on',
                try_on_category=form_data.get('try_on_category', 'top'),
                meta_title=form_data.get('meta_title', ''),
                meta_description=form_data.get('meta_description', ''),
            )
            
            # Handle image uploads
            for i, file_key in enumerate(['image1', 'image2', 'image3', 'image4']):
                if file_key in files:
                    ProductImage.objects.create(
                        product=product,
                        image=files[file_key],
                        alt_text=f"{product.name} - Image {i+1}",
                        is_primary=(i == 0),
                        sort_order=i
                    )
            
            messages.success(request, f'Product "{product.name}" created successfully!')
            return redirect('dashboard:product_management')
            
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
    
    context = {
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'dashboard/product_add.html', context)


@staff_member_required
def product_edit(request, product_id):
    """
    Edit an existing product.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form_data = request.POST
        files = request.FILES
        
        try:
            # Update product
            product.name = form_data.get('name')
            product.slug = form_data.get('slug')
            product.description = form_data.get('description', '')
            product.short_description = form_data.get('short_description', '')
            product.category_id = form_data.get('category')
            product.brand_id = form_data.get('brand')
            product.price = float(form_data.get('price', 0))
            product.sale_price = float(form_data.get('sale_price', 0)) if form_data.get('sale_price') else None
            product.stock_quantity = int(form_data.get('stock_quantity', 0))
            product.available_sizes = form_data.get('available_sizes', '')
            product.available_colors = form_data.get('available_colors', '')
            product.gender = form_data.get('gender', 'U')
            product.is_available = form_data.get('is_available') == 'on'
            product.is_featured = form_data.get('is_featured') == 'on'
            product.is_try_on_enabled = form_data.get('is_try_on_enabled') == 'on'
            product.try_on_category = form_data.get('try_on_category', 'top')
            product.meta_title = form_data.get('meta_title', '')
            product.meta_description = form_data.get('meta_description', '')
            product.save()
            
            # Handle new image uploads
            for i, file_key in enumerate(['image1', 'image2', 'image3', 'image4']):
                if file_key in files:
                    ProductImage.objects.create(
                        product=product,
                        image=files[file_key],
                        alt_text=f"{product.name} - Image {product.images.count() + 1}",
                        is_primary=False,
                        sort_order=product.images.count()
                    )
            
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('dashboard:product_management')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {
        'product': product,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'dashboard/product_edit.html', context)


@staff_member_required
def product_delete(request, product_id):
    """
    Delete a product.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('dashboard:product_management')
    
    context = {'product': product}
    return render(request, 'dashboard/product_delete.html', context)
