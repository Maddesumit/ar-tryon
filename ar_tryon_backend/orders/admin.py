"""
Admin configuration for orders app.
This configures how the order models appear in Django admin.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Sum, Count
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items"""
    model = CartItem
    extra = 0
    fields = ['product', 'quantity', 'selected_size', 'selected_color', 'unit_price', 'get_total_price']
    readonly_fields = ['get_total_price']
    
    def get_total_price(self, obj):
        if obj.pk:
            return f"₹{obj.get_total_price()}"
        return "-"
    get_total_price.short_description = 'Total Price'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model"""
    list_display = ['user', 'total_items', 'total_price_display', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_price_display']
    
    inlines = [CartItemInline]
    
    def total_price_display(self, obj):
        """Display total price in rupees"""
        return f"₹{obj.total_price}"
    total_price_display.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model"""
    list_display = ['cart_user', 'product', 'quantity', 'selected_size', 'selected_color', 'unit_price', 'total_price_display', 'created_at']
    list_filter = ['created_at', 'selected_size', 'selected_color']
    search_fields = ['cart__user__username', 'product__name']
    readonly_fields = ['total_price_display']
    
    def cart_user(self, obj):
        return obj.cart.user.username
    cart_user.short_description = 'User'
    
    def total_price_display(self, obj):
        return f"₹{obj.get_total_price()}"
    total_price_display.short_description = 'Total Price'


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    fields = ['product', 'product_name', 'quantity', 'selected_size', 'selected_color', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 
        'total_amount_display', 'created_at', 'items_count'
    ]
    list_filter = [
        'status', 'payment_status', 'created_at', 'shipping_state'
    ]
    search_fields = [
        'order_number', 'user__username', 'user__email', 
        'phone_number', 'email'
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 
        'total_amount_display', 'items_count'
    ]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'notes')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount_display'),
            'classes': ('collapse',)
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country')
        }),
        ('Billing Address', {
            'fields': ('billing_address', 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    # Custom actions
    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered']
    
    def total_amount_display(self, obj):
        """Display total amount in rupees"""
        return f"₹{obj.total_amount}"
    total_amount_display.short_description = 'Total Amount'
    
    def items_count(self, obj):
        """Show number of items in order"""
        return obj.items.count()
    items_count.short_description = 'Items'
    
    def mark_confirmed(self, request, queryset):
        """Bulk action to mark orders as confirmed"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} orders marked as confirmed.')
    mark_confirmed.short_description = "Mark selected orders as confirmed"
    
    def mark_shipped(self, request, queryset):
        """Bulk action to mark orders as shipped"""
        from django.utils import timezone
        updated = queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_delivered(self, request, queryset):
        """Bulk action to mark orders as delivered"""
        from django.utils import timezone
        updated = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_delivered.short_description = "Mark selected orders as delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model"""
    list_display = [
        'order_number', 'product_name', 'quantity', 
        'selected_size', 'selected_color', 'unit_price', 'total_price_display'
    ]
    list_filter = ['selected_size', 'selected_color', 'created_at']
    search_fields = [
        'order__order_number', 'product_name', 
        'order__user__username'
    ]
    readonly_fields = ['total_price_display']
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order Number'
    
    def total_price_display(self, obj):
        return f"₹{obj.total_price}"
    total_price_display.short_description = 'Total Price'


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    """Admin configuration for ShippingAddress model"""
    list_display = [
        'user', 'name', 'city', 'state', 'postal_code', 
        'is_default', 'created_at'
    ]
    list_filter = ['is_default', 'state', 'city', 'created_at']
    search_fields = [
        'user__username', 'name', 'address_line_1', 
        'city', 'state', 'postal_code'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'phone_number')
        }),
        ('Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Settings', {
            'fields': ('is_default',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
