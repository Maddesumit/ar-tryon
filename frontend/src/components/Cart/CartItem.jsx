import React, { useState } from 'react';
import { TrashIcon, PlusIcon, MinusIcon } from '@heroicons/react/24/outline';
import { useCart } from '../../contexts/CartContext';

const CartItem = ({ item, showControls = true }) => {
  const { updateCartItem, removeFromCart, loading } = useCart();
  const [isUpdating, setIsUpdating] = useState(false);

  const handleQuantityChange = async (newQuantity) => {
    if (newQuantity <= 0) {
      await handleRemove();
      return;
    }

    setIsUpdating(true);
    try {
      await updateCartItem(item.id, newQuantity);
    } catch (error) {
      console.error('Error updating quantity:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemove = async () => {
    setIsUpdating(true);
    try {
      await removeFromCart(item.id);
    } catch (error) {
      console.error('Error removing item:', error);
    } finally {
      setIsUpdating(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const itemTotal = parseFloat(item.product.price) * item.quantity;

  return (
    <div className={`flex items-center space-x-4 p-4 bg-white rounded-lg shadow-sm border ${isUpdating ? 'opacity-50' : ''}`}>
      {/* Product Image */}
      <div className="flex-shrink-0 w-20 h-20 bg-gray-200 rounded-lg overflow-hidden">
        {item.product.images && item.product.images.length > 0 ? (
          <img
            src={item.product.images[0].image}
            alt={item.product.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <span className="text-xs">No Image</span>
          </div>
        )}
      </div>

      {/* Product Details */}
      <div className="flex-grow">
        <h3 className="text-lg font-medium text-gray-900">{item.product.name}</h3>
        <p className="text-sm text-gray-500">
          {typeof item.product.brand === 'object' ? item.product.brand?.name : item.product.brand}
        </p>
        
        {/* Selected options */}
        <div className="flex space-x-4 mt-1 text-sm text-gray-600">
          {item.selected_size && (
            <span>Size: <strong>{item.selected_size}</strong></span>
          )}
          {item.selected_color && (
            <span>Color: <strong>{item.selected_color}</strong></span>
          )}
        </div>

        {/* Price */}
        <div className="mt-2">
          <span className="text-lg font-semibold text-gray-900">
            {formatPrice(item.product.price)}
          </span>
          <span className="text-sm text-gray-500 ml-2">
            each
          </span>
        </div>
      </div>

      {/* Quantity Controls */}
      {showControls && (
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => handleQuantityChange(item.quantity - 1)}
              disabled={isUpdating || loading || item.quantity <= 1}
              className="p-1 rounded bg-white shadow-sm hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <MinusIcon className="h-4 w-4" />
            </button>
            
            <span className="min-w-[2rem] text-center font-medium px-2">
              {item.quantity}
            </span>
            
            <button
              onClick={() => handleQuantityChange(item.quantity + 1)}
              disabled={isUpdating || loading}
              className="p-1 rounded bg-white shadow-sm hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PlusIcon className="h-4 w-4" />
            </button>
          </div>

          {/* Remove Button */}
          <button
            onClick={handleRemove}
            disabled={isUpdating || loading}
            className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Remove from cart"
          >
            <TrashIcon className="h-5 w-5" />
          </button>
        </div>
      )}

      {/* Item Total */}
      <div className="text-right">
        <div className="text-lg font-semibold text-gray-900">
          {formatPrice(itemTotal)}
        </div>
        <div className="text-sm text-gray-500">
          {item.quantity} × {formatPrice(item.product.price)}
        </div>
      </div>
    </div>
  );
};

export default CartItem;
