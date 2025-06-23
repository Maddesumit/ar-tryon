import React from 'react';
import { ShoppingCartIcon } from '@heroicons/react/24/outline';
import { ShoppingCartIcon as ShoppingCartSolidIcon } from '@heroicons/react/24/solid';
import { useCart } from '../../contexts/CartContext';
import { Link } from 'react-router-dom';

const CartIcon = ({ className = "", showBadge = true, solid = false }) => {
  const { getCartItemCount } = useCart();
  const itemCount = getCartItemCount();

  const IconComponent = solid ? ShoppingCartSolidIcon : ShoppingCartIcon;

  return (
    <Link to="/cart" className={`relative inline-flex items-center ${className}`}>
      <IconComponent className="h-6 w-6" />
      {showBadge && itemCount > 0 && (
        <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
          {itemCount > 99 ? '99+' : itemCount}
        </span>
      )}
    </Link>
  );
};

export default CartIcon;
