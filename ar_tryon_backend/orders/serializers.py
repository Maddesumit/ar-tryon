"""
Serializers for orders app.
These handle serialization of cart and order data for the API.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cart, CartItem, Order, OrderItem, ShippingAddress
from catalog.models import Product
from catalog.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 
            'selected_size', 'selected_color', 'unit_price', 
            'total_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        """Calculate total price for this cart item"""
        return obj.get_total_price()
    
    def validate_product_id(self, value):
        """Validate that product exists and is available"""
        try:
            product = Product.objects.get(id=value)
            if not product.is_available:
                raise serializers.ValidationError("This product is not available.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        if value > 99:
            raise serializers.ValidationError("Quantity cannot exceed 99.")
        return value
    
    def validate(self, data):
        """Validate product options"""
        product_id = data.get('product_id')
        selected_size = data.get('selected_size')
        selected_color = data.get('selected_color')
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                
                # Validate size if provided
                if selected_size:
                    available_sizes = [size.strip() for size in product.available_sizes.split(',')]
                    if selected_size not in available_sizes:
                        raise serializers.ValidationError({
                            'selected_size': f"Size '{selected_size}' is not available. Available sizes: {', '.join(available_sizes)}"
                        })
                
                # Validate color if provided
                if selected_color:
                    available_colors = [color.strip() for color in product.available_colors.split(',')]
                    if selected_color not in available_colors:
                        raise serializers.ValidationError({
                            'selected_color': f"Color '{selected_color}' is not available. Available colors: {', '.join(available_colors)}"
                        })
                        
            except Product.DoesNotExist:
                pass  # Will be caught by product_id validation
        
        return data


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    is_empty = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 
            'total_price', 'is_empty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_total_items(self, obj):
        """Get total number of items in cart"""
        return obj.total_items
    
    def get_total_price(self, obj):
        """Get total price of cart"""
        return obj.total_price
    
    def get_is_empty(self, obj):
        """Check if cart is empty"""
        return obj.is_empty


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=99, default=1)
    selected_size = serializers.CharField(max_length=10, required=False, allow_blank=True)
    selected_color = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_product_id(self, value):
        """Validate that product exists and is available"""
        try:
            product = Product.objects.get(id=value)
            if not product.is_available:
                raise serializers.ValidationError("This product is not available.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1, max_value=99)


class ShippingAddressSerializer(serializers.ModelSerializer):
    """Serializer for shipping addresses"""
    
    class Meta:
        model = ShippingAddress
        fields = [
            'id', 'name', 'address_line_1', 'address_line_2', 
            'city', 'state', 'postal_code', 'country', 
            'phone_number', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_postal_code(self, value):
        """Validate Indian postal code format"""
        import re
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("Please enter a valid 6-digit postal code.")
        return value
    
    def validate_phone_number(self, value):
        """Validate Indian phone number format"""
        import re
        if not re.match(r'^[6-9]\d{9}$', value):
            raise serializers.ValidationError("Please enter a valid 10-digit Indian mobile number.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 
            'selected_size', 'selected_color', 'unit_price', 
            'total_price', 'created_at'
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'payment_status',
            'subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount',
            'shipping_address', 'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'billing_address', 'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
            'phone_number', 'email', 'notes', 'items',
            'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'created_at', 'updated_at', 
            'shipped_at', 'delivered_at'
        ]


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    shipping_address_id = serializers.IntegerField()
    billing_same_as_shipping = serializers.BooleanField(default=True)
    billing_address_id = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(max_length=15)
    email = serializers.EmailField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_shipping_address_id(self, value):
        """Validate shipping address belongs to user"""
        user = self.context['request'].user
        try:
            address = ShippingAddress.objects.get(id=value, user=user)
            return value
        except ShippingAddress.DoesNotExist:
            raise serializers.ValidationError("Invalid shipping address.")
    
    def validate_billing_address_id(self, value):
        """Validate billing address belongs to user"""
        if value:
            user = self.context['request'].user
            try:
                address = ShippingAddress.objects.get(id=value, user=user)
                return value
            except ShippingAddress.DoesNotExist:
                raise serializers.ValidationError("Invalid billing address.")
        return value
    
    def validate(self, data):
        """Validate billing address is provided if not same as shipping"""
        if not data.get('billing_same_as_shipping') and not data.get('billing_address_id'):
            raise serializers.ValidationError({
                'billing_address_id': 'Billing address is required when not same as shipping.'
            })
        return data
