"""
URL patterns for orders API endpoints.
"""

from django.urls import path
from . import api_views

app_name = 'orders'

urlpatterns = [
    # Cart endpoints
    path('cart/', api_views.get_cart, name='get_cart'),
    path('cart/add/', api_views.add_to_cart, name='add_to_cart'),
    path('cart/item/<int:item_id>/update/', api_views.update_cart_item, name='update_cart_item'),
    path('cart/item/<int:item_id>/remove/', api_views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', api_views.clear_cart, name='clear_cart'),
    
    # Shipping address endpoints
    path('addresses/', api_views.ShippingAddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', api_views.ShippingAddressDetailView.as_view(), name='address_detail'),
    path('addresses/<int:address_id>/set-default/', api_views.set_default_address, name='set_default_address'),
    
    # Order endpoints
    path('orders/', api_views.OrderListView.as_view(), name='order_list'),
    path('orders/create/', api_views.create_order, name='create_order'),
    path('orders/<str:order_number>/', api_views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<str:order_number>/cancel/', api_views.cancel_order, name='cancel_order'),
]
