import React, { useState } from 'react';
import { PlusIcon, MinusIcon, ShoppingCartIcon } from '@heroicons/react/24/outline';
import { useCart } from '../../contexts/CartContext';

const AddToCartButton = ({ 
  product, 
  className = "", 
  size = "medium",
  showQuantitySelector = false,
  selectedSize = null,
  selectedColor = null,
  disabled = false
}) => {
  const { addToCart, isInCart, getCartItem, updateCartItem, loading } = useCart();
  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);

  const cartItem = getCartItem(product.id);
  const inCart = isInCart(product.id);

  const handleAddToCart = async () => {
    console.log('🛒 AddToCartButton: handleAddToCart called');
    console.log('📦 Product:', product);
    console.log('📊 Quantity:', quantity);
    console.log('📏 Selected size:', selectedSize);
    console.log('🎨 Selected color:', selectedColor);
    
    setIsAdding(true);
    try {
      console.log('🚀 Calling addToCart from context...');
      await addToCart(product, quantity, selectedSize, selectedColor);
      console.log('✅ addToCart completed successfully');
      setQuantity(1); // Reset quantity after adding
    } catch (error) {
      console.error('❌ AddToCartButton: Error adding to cart:', error);
      // You might want to show a toast/notification here
      alert('Failed to add item to cart. Please try again.');
    } finally {
      setIsAdding(false);
    }
  };

  const handleUpdateQuantity = async (newQuantity) => {
    if (cartItem && newQuantity > 0) {
      await updateCartItem(cartItem.id, newQuantity);
    }
  };

  const sizeClasses = {
    small: "px-3 py-1.5 text-sm",
    medium: "px-4 py-2 text-base",
    large: "px-6 py-3 text-lg"
  };

  const baseClasses = `
    inline-flex items-center justify-center
    font-medium rounded-lg
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    ${sizeClasses[size]}
    ${className}
  `;

  if (inCart && showQuantitySelector && cartItem) {
    return (
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handleUpdateQuantity(cartItem.quantity - 1)}
          disabled={loading || cartItem.quantity <= 1}
          className="p-1 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors duration-200 disabled:opacity-50"
        >
          <MinusIcon className="h-4 w-4" />
        </button>
        
        <span className="min-w-[2rem] text-center font-medium">
          {cartItem.quantity}
        </span>
        
        <button
          onClick={() => handleUpdateQuantity(cartItem.quantity + 1)}
          disabled={loading}
          className="p-1 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors duration-200 disabled:opacity-50"
        >
          <PlusIcon className="h-4 w-4" />
        </button>
      </div>
    );
  }

  if (inCart) {
    return (
      <button
        disabled={true}
        className={`${baseClasses} bg-green-100 text-green-800 border border-green-300`}
      >
        <ShoppingCartIcon className="h-5 w-5 mr-2" />
        In Cart
      </button>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      {showQuantitySelector && (
        <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setQuantity(Math.max(1, quantity - 1))}
            disabled={quantity <= 1}
            className="p-1 rounded bg-white shadow-sm hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50"
          >
            <MinusIcon className="h-4 w-4" />
          </button>
          
          <span className="min-w-[2rem] text-center font-medium px-2">
            {quantity}
          </span>
          
          <button
            onClick={() => setQuantity(quantity + 1)}
            className="p-1 rounded bg-white shadow-sm hover:bg-gray-50 transition-colors duration-200"
          >
            <PlusIcon className="h-4 w-4" />
          </button>
        </div>
      )}
      
      <button
        onClick={handleAddToCart}
        disabled={disabled || loading || isAdding}
        className={`${baseClasses} bg-blue-600 hover:bg-blue-700 text-white shadow-sm hover:shadow-md`}
      >
        {isAdding ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Adding...
          </>
        ) : (
          <>
            <ShoppingCartIcon className="h-5 w-5 mr-2" />
            Add to Cart
          </>
        )}
      </button>
    </div>
  );
};

export default AddToCartButton;
