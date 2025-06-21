"""
Admin configuration for catalog app.
This configures how the catalog models appear in Django admin.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg
from django.contrib.admin import SimpleListFilter
from .models import Category, Brand, Product, ProductImage, ProductReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""
    list_display = ['name', 'slug', 'is_active', 'sort_order', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}  # Auto-generate slug from name
    ordering = ['sort_order', 'name']
    
    def product_count(self, obj):
        """Show number of products in this category"""
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model"""
    list_display = ['name', 'slug', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        """Show number of products for this brand"""
        return obj.products.count()
    product_count.short_description = 'Products'

class ProductImageInline(admin.TabularInline):
    """Inline admin for product images"""
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order', 'image_preview']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Show small preview of the image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 80px; max-width: 80px; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

class ProductReviewInline(admin.TabularInline):
    """Inline admin for product reviews"""
    model = ProductReview
    extra = 0
    fields = ['user', 'rating', 'comment', 'is_verified', 'created_at']
    readonly_fields = ['created_at']
    
class PriceRangeFilter(SimpleListFilter):
    """Custom filter for product price ranges"""
    title = 'Price Range'
    parameter_name = 'price_range'
    
    def lookups(self, request, model_admin):
        return (
            ('0-50', '$0 - $50'),
            ('50-100', '$50 - $100'),
            ('100-200', '$100 - $200'),
            ('200+', '$200+'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == '0-50':
            return queryset.filter(price__lte=50)
        if self.value() == '50-100':
            return queryset.filter(price__gt=50, price__lte=100)
        if self.value() == '100-200':
            return queryset.filter(price__gt=100, price__lte=200)
        if self.value() == '200+':
            return queryset.filter(price__gt=200)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Enhanced admin configuration for Product model"""
    list_display = [
        'image_thumbnail', 'name', 'brand', 'category', 'current_price', 'sale_badge',
        'stock_status', 'is_try_on_enabled', 'image_count', 'created_at'
    ]
    list_filter = [
        'category', 'brand', 'gender', 'is_available', 'is_try_on_enabled', 
        'is_featured', 'try_on_category', PriceRangeFilter, 'created_at'
    ]
    search_fields = ['name', 'description', 'short_description', 'brand__name', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    
    # Organize fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'short_description', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'brand', 'gender')
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price'),
            'description': 'Set the regular price and optional sale price for discounts.'
        }),
        ('Product Details', {
            'fields': ('available_sizes', 'available_colors', 'stock_quantity')
        }),
        ('Try-On Settings', {
            'fields': ('is_try_on_enabled', 'try_on_category'),
            'description': 'Configure virtual try-on capabilities for this product.'
        }),
        ('Status & SEO', {
            'fields': ('is_available', 'is_featured', 'meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    # Add inline for product images and reviews
    inlines = [ProductImageInline, ProductReviewInline]
    
    # Custom actions
    actions = ['make_available', 'make_unavailable', 'enable_try_on', 'disable_try_on', 'mark_featured']
    
    # Custom display methods
    def image_thumbnail(self, obj):
        """Show thumbnail of primary product image"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 4px;" />',
                primary_image.image.url
            )
        return format_html('<div style="width: 50px; height: 50px; background: #f0f0f0; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px;">No Image</div>')
    image_thumbnail.short_description = 'Image'
    
    def current_price(self, obj):
        """Display current price with sale indication"""
        if obj.is_on_sale:
            return format_html(
                '<span style="color: red; font-weight: bold;">${}</span> <small style="text-decoration: line-through;">${}</small>',
                obj.sale_price, obj.price
            )
        return f'${obj.price}'
    current_price.short_description = 'Price'
    
    def sale_badge(self, obj):
        """Show sale badge if product is on sale"""
        if obj.is_on_sale:
            return format_html('<span style="background: red; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px;">SALE</span>')
        return ''
    sale_badge.short_description = 'Sale'
    
    def stock_status(self, obj):
        """Show stock status with color coding"""
        if obj.stock_quantity == 0:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.stock_quantity < 10:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock_quantity)
        else:
            return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock'
    
    def image_count(self, obj):
        """Show number of images for this product"""
        count = obj.images.count()
        if count == 0:
            return format_html('<span style="color: red;">0</span>')
        return count
    image_count.short_description = 'Images'
    
    # Bulk actions
    def make_available(self, request, queryset):
        """Bulk action to make products available"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} products marked as available.')
    make_available.short_description = "Mark selected products as available"
    
    def make_unavailable(self, request, queryset):
        """Bulk action to make products unavailable"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} products marked as unavailable.')
    make_unavailable.short_description = "Mark selected products as unavailable"
    
    def enable_try_on(self, request, queryset):
        """Bulk action to enable try-on for products"""
        updated = queryset.update(is_try_on_enabled=True)
        self.message_user(request, f'{updated} products enabled for try-on.')
    enable_try_on.short_description = "Enable try-on for selected products"
    
    def disable_try_on(self, request, queryset):
        """Bulk action to disable try-on for products"""
        updated = queryset.update(is_try_on_enabled=False)
        self.message_user(request, f'{updated} products disabled for try-on.')
    disable_try_on.short_description = "Disable try-on for selected products"
    
    def mark_featured(self, request, queryset):
        """Bulk action to mark products as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products marked as featured.')
    mark_featured.short_description = "Mark selected products as featured"
    
    def current_price(self, obj):
        """Display current price (sale price if available)"""
        if obj.is_on_sale:
            return f"${obj.sale_price} (was ${obj.price})"
        return f"${obj.price}"
    current_price.short_description = 'Current Price'
    
    def is_on_sale(self, obj):
        """Show if product is on sale"""
        return obj.is_on_sale
    is_on_sale.boolean = True
    is_on_sale.short_description = 'On Sale'

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin configuration for ProductImage model"""
    list_display = ['product', 'image_preview', 'alt_text', 'is_primary', 'sort_order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    ordering = ['product', 'sort_order']
    
    def image_preview(self, obj):
        """Show preview of the image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ProductReview model"""
    list_display = [
        'product', 'user', 'rating_stars', 'title', 'is_approved', 
        'is_verified_purchase', 'created_at'
    ]
    list_filter = [
        'rating', 'is_approved', 'is_verified_purchase', 'created_at'
    ]
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def rating_stars(self, obj):
        """Display rating as stars"""
        full_stars = '★' * obj.rating
        empty_stars = '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: gold;">{}</span><span style="color: #ddd;">{}</span> ({})',
            full_stars, empty_stars, obj.rating
        )
    rating_stars.short_description = 'Rating'
    
    def approve_reviews(self, request, queryset):
        """Bulk action to approve reviews"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        """Bulk action to disapprove reviews"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews disapproved.')
    disapprove_reviews.short_description = "Disapprove selected reviews"

# Customize admin site
admin.site.site_header = "AR Try-On Admin Dashboard"
admin.site.site_title = "AR Try-On Admin"
admin.site.index_title = "Welcome to AR Try-On Administration"
