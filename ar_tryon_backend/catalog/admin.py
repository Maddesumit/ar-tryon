"""
Admin configuration for catalog app.
This configures how the catalog models appear in Django admin.
"""

from django.contrib import admin
from django.utils.html import format_html
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
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Show small preview of the image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Preview'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model"""
    list_display = [
        'name', 'brand', 'category', 'current_price', 'is_on_sale', 
        'stock_quantity', 'is_available', 'is_try_on_enabled', 'created_at'
    ]
    list_filter = [
        'category', 'brand', 'gender', 'is_available', 'is_try_on_enabled', 
        'is_featured', 'try_on_category', 'created_at'
    ]
    search_fields = ['name', 'description', 'short_description']
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
            'fields': ('price', 'sale_price')
        }),
        ('Product Details', {
            'fields': ('available_sizes', 'available_colors', 'stock_quantity')
        }),
        ('Try-On Settings', {
            'fields': ('is_try_on_enabled', 'try_on_category')
        }),
        ('Status & SEO', {
            'fields': ('is_available', 'is_featured', 'meta_title', 'meta_description'),
            'classes': ('collapse',)  # Make this section collapsible
        }),
    )
    
    # Add inline for product images
    inlines = [ProductImageInline]
    
    # Custom actions
    actions = ['make_available', 'make_unavailable', 'enable_try_on']
    
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
        'product', 'user', 'rating', 'title', 'is_approved', 
        'is_verified_purchase', 'created_at'
    ]
    list_filter = [
        'rating', 'is_approved', 'is_verified_purchase', 'created_at'
    ]
    search_fields = ['product__name', 'user__username', 'title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    # Organize fields
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'title', 'content')
        }),
        ('Purchase Details', {
            'fields': ('size_purchased', 'color_purchased', 'is_verified_purchase')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'unapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        """Bulk approve reviews"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved.')
    approve_reviews.short_description = "Approve selected reviews"
    
    def unapprove_reviews(self, request, queryset):
        """Bulk unapprove reviews"""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews unapproved.')
    unapprove_reviews.short_description = "Unapprove selected reviews"
