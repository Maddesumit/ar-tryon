import React, { useState, useRef, useEffect } from 'react';
import { ShoppingCartIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useCart } from '../../contexts/CartContext';
import { Link } from 'react-router-dom';

const MiniCart = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const { items, total, getCartItemCount, loading } = useCart();
  const itemCount = getCartItemCount();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Cart Icon Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg transition-colors duration-200"
      >
        <ShoppingCartIcon className="h-6 w-6" />
        {itemCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
            {itemCount > 99 ? '99+' : itemCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Shopping Cart ({itemCount})
            </h3>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 text-gray-400 hover:text-gray-600 rounded-full transition-colors duration-200"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Cart Items */}
          <div className="max-h-64 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-sm text-gray-500">Loading cart...</p>
              </div>
            ) : items.length === 0 ? (
              <div className="p-4 text-center">
                <ShoppingCartIcon className="h-12 w-12 text-gray-300 mx-auto mb-2" />
                <p className="text-gray-500">Your cart is empty</p>
              </div>
            ) : (
              <div className="p-2">
                {items.slice(0, 3).map((item) => (
                  <div key={item.id} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded-lg">
                    {/* Product Image */}
                    <div className="flex-shrink-0 w-12 h-12 bg-gray-200 rounded-lg overflow-hidden">
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

                    {/* Product Info */}
                    <div className="flex-grow min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.product.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {item.quantity} × {formatPrice(item.product.price)}
                      </p>
                    </div>

                    {/* Item Total */}
                    <div className="text-sm font-medium text-gray-900">
                      {formatPrice(parseFloat(item.product.price) * item.quantity)}
                    </div>
                  </div>
                ))}

                {items.length > 3 && (
                  <div className="p-2 text-center text-sm text-gray-500">
                    ... and {items.length - 3} more items
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          {items.length > 0 && (
            <div className="p-4 border-t border-gray-200 bg-gray-50">
              {/* Total */}
              <div className="flex justify-between items-center mb-3">
                <span className="text-base font-medium text-gray-900">Total:</span>
                <span className="text-lg font-semibold text-gray-900">
                  {formatPrice(total)}
                </span>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2">
                <Link
                  to="/cart"
                  onClick={() => setIsOpen(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded-lg text-center text-sm font-medium transition-colors duration-200"
                >
                  View Cart
                </Link>
                <Link
                  to="/checkout"
                  onClick={() => setIsOpen(false)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-center text-sm font-medium transition-colors duration-200"
                >
                  Checkout
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MiniCart;
