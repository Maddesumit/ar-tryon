"""
API views for orders and shopping cart functionality.
"""

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem, ShippingAddress
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, ShippingAddressSerializer,
    OrderSerializer, CreateOrderSerializer
)
from catalog.models import Product


# ============ CART VIEWS ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """
    Get or create user's shopping cart.
    """
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Add item to shopping cart or update quantity if already exists.
    """
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        selected_size = serializer.validated_data.get('selected_size', '')
        selected_color = serializer.validated_data.get('selected_color', '')
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Get product
        product = get_object_or_404(Product, id=product_id)
        
        # Check if item already exists with same options
        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product=product,
                selected_size=selected_size,
                selected_color=selected_color
            )
            # Update quantity
            cart_item.quantity += quantity
            if cart_item.quantity > 99:
                cart_item.quantity = 99
            cart_item.save()
            message = "Cart item quantity updated"
        except CartItem.DoesNotExist:
            # Create new cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity,
                selected_size=selected_size,
                selected_color=selected_color,
                unit_price=product.sale_price or product.price
            )
            message = "Item added to cart"
        
        # Return updated cart
        cart_serializer = CartSerializer(cart)
        return Response({
            'message': message,
            'cart': cart_serializer.data
        }, status=status.HTTP_200_OK)
    
    # 🔍 DEBUG: Print serializer errors
    print("❌ Serializer validation failed!")
    print("❌ Errors:", serializer.errors)
    print("❌ Received data:", request.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Update cart item quantity.
    """
    cart_item = get_object_or_404(
        CartItem, 
        id=item_id, 
        cart__user=request.user
    )
    
    serializer = UpdateCartItemSerializer(data=request.data)
    if serializer.is_valid():
        cart_item.quantity = serializer.validated_data['quantity']
        cart_item.save()
        
        # Return updated cart
        cart_serializer = CartSerializer(cart_item.cart)
        return Response({
            'message': 'Cart item updated',
            'cart': cart_serializer.data
        })
    
    # 🔍 DEBUG: Print serializer errors
    print("❌ Serializer validation failed!")
    print("❌ Errors:", serializer.errors)
    print("❌ Received data:", request.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """
    Remove item from cart.
    """
    cart_item = get_object_or_404(
        CartItem, 
        id=item_id, 
        cart__user=request.user
    )
    
    cart = cart_item.cart
    cart_item.delete()
    
    # Return updated cart
    cart_serializer = CartSerializer(cart)
    return Response({
        'message': 'Item removed from cart',
        'cart': cart_serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """
    Clear all items from cart.
    """
    try:
        cart = Cart.objects.get(user=request.user)
        cart.items.all().delete()
        
        cart_serializer = CartSerializer(cart)
        return Response({
            'message': 'Cart cleared',
            'cart': cart_serializer.data
        })
    except Cart.DoesNotExist:
        return Response({
            'message': 'Cart is already empty'
        })


# ============ SHIPPING ADDRESS VIEWS ============

class ShippingAddressListCreateView(generics.ListCreateAPIView):
    """
    List user's shipping addresses or create a new one.
    """
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ShippingAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a shipping address.
    """
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_default_address(request, address_id):
    """
    Set an address as default.
    """
    address = get_object_or_404(
        ShippingAddress, 
        id=address_id, 
        user=request.user
    )
    
    # Remove default from other addresses
    ShippingAddress.objects.filter(
        user=request.user, 
        is_default=True
    ).update(is_default=False)
    
    # Set this address as default
    address.is_default = True
    address.save()
    
    return Response({
        'message': 'Default address updated'
    })


# ============ ORDER VIEWS ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Create order from cart items.
    """
    serializer = CreateOrderSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
            if cart.is_empty:
                return Response({
                    'error': 'Cart is empty'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({
                'error': 'Cart not found'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get addresses
        shipping_address = get_object_or_404(
            ShippingAddress, 
            id=serializer.validated_data['shipping_address_id'],
            user=request.user
        )
        
        if serializer.validated_data['billing_same_as_shipping']:
            billing_address = shipping_address
        else:
            billing_address = get_object_or_404(
                ShippingAddress,
                id=serializer.validated_data['billing_address_id'],
                user=request.user
            )
        
        # Create order in transaction
        with transaction.atomic():
            # Calculate totals
            subtotal = cart.total_price
            tax_amount = subtotal * Decimal('0.18')  # 18% GST
            shipping_amount = Decimal('50.00') if subtotal < Decimal('500.00') else Decimal('0.00')  # Free shipping above ₹500
            total_amount = subtotal + tax_amount + shipping_amount
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                subtotal=subtotal,
                tax_amount=tax_amount,
                shipping_amount=shipping_amount,
                total_amount=total_amount,
                
                # Shipping info
                shipping_address=shipping_address.address_line_1,
                shipping_city=shipping_address.city,
                shipping_state=shipping_address.state,
                shipping_postal_code=shipping_address.postal_code,
                shipping_country=shipping_address.country,
                
                # Billing info
                billing_address=billing_address.address_line_1,
                billing_city=billing_address.city,
                billing_state=billing_address.state,
                billing_postal_code=billing_address.postal_code,
                billing_country=billing_address.country,
                
                # Contact info
                phone_number=serializer.validated_data['phone_number'],
                email=serializer.validated_data['email'],
                notes=serializer.validated_data.get('notes', '')
            )
            
            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    selected_size=cart_item.selected_size,
                    selected_color=cart_item.selected_color,
                    unit_price=cart_item.unit_price,
                    total_price=cart_item.get_total_price()
                )
            
            # Clear cart
            cart.items.all().delete()
        
        # Return created order
        order_serializer = OrderSerializer(order)
        return Response({
            'message': 'Order created successfully',
            'order': order_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    # 🔍 DEBUG: Print serializer errors
    print("❌ Serializer validation failed!")
    print("❌ Errors:", serializer.errors)
    print("❌ Received data:", request.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    """
    List user's orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific order.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    lookup_field = 'order_number'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_number):
    """
    Cancel an order (only if pending or confirmed).
    """
    order = get_object_or_404(
        Order, 
        order_number=order_number, 
        user=request.user
    )
    
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'message': 'Order cancelled successfully'
        })
    else:
        return Response({
            'error': 'Order cannot be cancelled at this stage'
        }, status=status.HTTP_400_BAD_REQUEST)
