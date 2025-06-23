import React from 'react';
import { useCart } from '../../contexts/CartContext';

const OrderSummary = ({ shippingAddress, showEditButton = false, onEdit }) => {
  const { items, total, getCartItemCount } = useCart();
  const itemCount = getCartItemCount();

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const subtotal = total;
  const shipping = 0; // Free shipping
  const tax = subtotal * 0.18; // 18% GST
  const finalTotal = subtotal + shipping + tax;

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-6">Order Summary</h2>
      
      {/* Items List */}
      <div className="space-y-4 mb-6">
        {items.map((item) => (
          <div key={item.id} className="flex items-center space-x-4">
            {/* Product Image */}
            <div className="flex-shrink-0 w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
              {item.product.images && item.product.images.length > 0 ? (
                <img
                  src={item.product.images[0].image}
                  alt={item.product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400 text-xs">
                  No Image
                </div>
              )}
            </div>

            {/* Product Details */}
            <div className="flex-grow min-w-0">
              <h3 className="text-sm font-medium text-gray-900 truncate">
                {item.product.name}
              </h3>
              <p className="text-sm text-gray-500">
                {typeof item.product.brand === 'object' ? item.product.brand?.name : item.product.brand}
              </p>
              <div className="flex space-x-2 text-xs text-gray-600 mt-1">
                {item.selected_size && (
                  <span>Size: {item.selected_size}</span>
                )}
                {item.selected_color && (
                  <span>Color: {item.selected_color}</span>
                )}
              </div>
            </div>

            {/* Quantity and Price */}
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {formatPrice(parseFloat(item.product.price) * item.quantity)}
              </p>
              <p className="text-xs text-gray-500">
                Qty: {item.quantity}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Pricing Breakdown */}
      <div className="border-t border-gray-200 pt-4 space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Subtotal ({itemCount} items)</span>
          <span className="font-medium">{formatPrice(subtotal)}</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Shipping</span>
          <span className="text-green-600 font-medium">Free</span>
        </div>
        
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">GST (18%)</span>
          <span className="font-medium">{formatPrice(tax)}</span>
        </div>
        
        <div className="border-t border-gray-200 pt-3">
          <div className="flex justify-between">
            <span className="text-base font-medium text-gray-900">Total</span>
            <span className="text-xl font-semibold text-gray-900">{formatPrice(finalTotal)}</span>
          </div>
        </div>
      </div>

      {/* Shipping Address */}
      {shippingAddress && (
        <div className="border-t border-gray-200 pt-6 mt-6">
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-sm font-medium text-gray-900">Shipping to:</h3>
            {showEditButton && onEdit && (
              <button
                onClick={onEdit}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Edit
              </button>
            )}
          </div>
          <div className="text-sm text-gray-600">
            <p className="font-medium text-gray-900">
              {shippingAddress.first_name} {shippingAddress.last_name}
            </p>
            {shippingAddress.company && (
              <p>{shippingAddress.company}</p>
            )}
            <p>{shippingAddress.address_line_1}</p>
            {shippingAddress.address_line_2 && (
              <p>{shippingAddress.address_line_2}</p>
            )}
            <p>
              {shippingAddress.city}, {shippingAddress.state} {shippingAddress.postal_code}
            </p>
            <p>{shippingAddress.country}</p>
            {shippingAddress.phone_number && (
              <p>Phone: {shippingAddress.phone_number}</p>
            )}
          </div>
        </div>
      )}

      {/* Security Notice */}
      <div className="border-t border-gray-200 pt-4 mt-6">
        <div className="flex items-center justify-center text-xs text-gray-500">
          <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Secure checkout with 256-bit SSL encryption
        </div>
      </div>
    </div>
  );
};

export default OrderSummary;
