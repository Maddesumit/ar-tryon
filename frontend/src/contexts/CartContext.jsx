import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useAuth } from './AuthContext';
import api from '../services/api';

const CartContext = createContext();

// Cart action types
const CART_ACTIONS = {
  SET_CART: 'SET_CART',
  ADD_ITEM: 'ADD_ITEM',
  UPDATE_ITEM: 'UPDATE_ITEM',
  REMOVE_ITEM: 'REMOVE_ITEM',
  CLEAR_CART: 'CLEAR_CART',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Cart reducer
const cartReducer = (state, action) => {
  switch (action.type) {
    case CART_ACTIONS.SET_CART:
      return {
        ...state,
        items: action.payload.items || [],
        total: action.payload.total || 0,
        loading: false,
        error: null
      };
    
    case CART_ACTIONS.ADD_ITEM:
      const existingItem = state.items.find(item => item.product.id === action.payload.product.id);
      if (existingItem) {
        return {
          ...state,
          items: state.items.map(item =>
            item.product.id === action.payload.product.id
              ? { ...item, quantity: item.quantity + action.payload.quantity }
              : item
          ),
          loading: false
        };
      } else {
        return {
          ...state,
          items: [...state.items, action.payload],
          loading: false
        };
      }
    
    case CART_ACTIONS.UPDATE_ITEM:
      return {
        ...state,
        items: state.items.map(item =>
          item.id === action.payload.id
            ? { ...item, quantity: action.payload.quantity }
            : item
        ),
        loading: false
      };
    
    case CART_ACTIONS.REMOVE_ITEM:
      return {
        ...state,
        items: state.items.filter(item => item.id !== action.payload.id),
        loading: false
      };
    
    case CART_ACTIONS.CLEAR_CART:
      return {
        ...state,
        items: [],
        total: 0,
        loading: false
      };
    
    case CART_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };
    
    case CART_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };
    
    case CART_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    
    default:
      return state;
  }
};

// Initial cart state
const initialState = {
  items: [],
  total: 0,
  loading: false,
  error: null
};

export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialState);
  const { user, isAuthenticated } = useAuth();

  // Calculate total whenever items change
  useEffect(() => {
    const total = state.items.reduce((sum, item) => {
      return sum + (parseFloat(item.product.price) * item.quantity);
    }, 0);
    
    if (total !== state.total) {
      dispatch({ type: CART_ACTIONS.SET_CART, payload: { ...state, total } });
    }
  }, [state.items]);

  // Load cart from backend when user is authenticated
  useEffect(() => {
    if (isAuthenticated && user) {
      loadCartFromBackend();
    } else {
      loadCartFromLocalStorage();
    }
  }, [isAuthenticated, user]);

  // Load cart from backend
  const loadCartFromBackend = async () => {
    console.log('🔄 loadCartFromBackend called');
    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      console.log('📡 Making API call to /orders/cart/');
      
      const response = await api.get('/orders/cart/');
      console.log('✅ Backend cart response:', response.data);
      
      dispatch({ 
        type: CART_ACTIONS.SET_CART, 
        payload: {
          items: response.data.items || [],
          total: response.data.total || 0
        }
      });
      console.log('✅ Cart state updated');
    } catch (error) {
      console.error('❌ Error loading cart from backend:', error);
      console.error('❌ Error response:', error.response);
      // Fallback to localStorage if backend fails
      loadCartFromLocalStorage();
    }
  };

  // Load cart from localStorage
  const loadCartFromLocalStorage = () => {
    try {
      const savedCart = localStorage.getItem('cart');
      if (savedCart) {
        const parsedCart = JSON.parse(savedCart);
        dispatch({ 
          type: CART_ACTIONS.SET_CART, 
          payload: parsedCart 
        });
      }
    } catch (error) {
      console.error('Error loading cart from localStorage:', error);
      dispatch({ type: CART_ACTIONS.SET_ERROR, payload: 'Failed to load cart' });
    }
  };

  // Save cart to localStorage
  const saveCartToLocalStorage = (cartData) => {
    try {
      localStorage.setItem('cart', JSON.stringify(cartData));
    } catch (error) {
      console.error('Error saving cart to localStorage:', error);
    }
  };

  // Add item to cart
  const addToCart = async (product, quantity = 1, selectedSize = null, selectedColor = null) => {
    console.log('🚀 CartContext: addToCart called');
    console.log('📦 Product:', product);
    console.log('📊 Quantity:', quantity);
    console.log('🔐 Is Authenticated:', isAuthenticated);
    console.log('👤 User:', user);
    
    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: CART_ACTIONS.CLEAR_ERROR });

      const itemData = {
        product,
        quantity,
        selected_size: selectedSize,
        selected_color: selectedColor
      };

      console.log('🔍 Adding to cart - Product ID:', product.id, 'Quantity:', quantity);
    
    
      if (isAuthenticated) {
        console.log('✅ User authenticated, adding to backend cart');
        
        const requestData = {
          product_id: product.id,
          quantity,
          selected_size: selectedSize || '',
          selected_color: selectedColor || ''
        };
        
        console.log('📤 Request data:', requestData);
        console.log('🌐 API URL:', '/orders/cart/add/');
        
        // Add to backend cart
        const response = await api.post('/orders/cart/add/', requestData);
        
        console.log('✅ Backend response:', response.data);
        
        // Reload cart from backend to get updated data
        console.log('🔄 Reloading cart from backend...');
        await loadCartFromBackend();
        console.log('✅ Cart reloaded successfully');
      } else {
        console.log('❌ User not authenticated, adding to local cart');
        // Add to local cart
        dispatch({ type: CART_ACTIONS.ADD_ITEM, payload: itemData });
        const newCartData = {
          items: [...state.items, itemData],
          total: state.total
        };
        saveCartToLocalStorage(newCartData);
      }
    } catch (error) {
      console.error('❌ Error adding to cart:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error data:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      
      dispatch({ 
        type: CART_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.message || 'Failed to add item to cart' 
      });
      
      // Re-throw error so AddToCartButton can handle it
      throw error;
    }
  };

  // Update item quantity
  const updateCartItem = async (itemId, quantity) => {
    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: CART_ACTIONS.CLEAR_ERROR });

      if (quantity <= 0) {
        await removeFromCart(itemId);
        return;
      }

      if (isAuthenticated) {
        await api.patch(`/orders/cart/items/${itemId}/`, { quantity });
        await loadCartFromBackend();
      } else {
        dispatch({ 
          type: CART_ACTIONS.UPDATE_ITEM, 
          payload: { id: itemId, quantity } 
        });
        const updatedItems = state.items.map(item =>
          item.id === itemId ? { ...item, quantity } : item
        );
        saveCartToLocalStorage({ items: updatedItems, total: state.total });
      }
    } catch (error) {
      console.error('Error updating cart item:', error);
      dispatch({ 
        type: CART_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.message || 'Failed to update cart item' 
      });
    }
  };

  // Remove item from cart
  const removeFromCart = async (itemId) => {
    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: CART_ACTIONS.CLEAR_ERROR });

      if (isAuthenticated) {
        await api.delete(`/orders/cart/items/${itemId}/`);
        await loadCartFromBackend();
      } else {
        dispatch({ type: CART_ACTIONS.REMOVE_ITEM, payload: { id: itemId } });
        const updatedItems = state.items.filter(item => item.id !== itemId);
        saveCartToLocalStorage({ items: updatedItems, total: state.total });
      }
    } catch (error) {
      console.error('Error removing from cart:', error);
      dispatch({ 
        type: CART_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.message || 'Failed to remove item from cart' 
      });
    }
  };

  // Clear entire cart
  const clearCart = async () => {
    try {
      dispatch({ type: CART_ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: CART_ACTIONS.CLEAR_ERROR });

      if (isAuthenticated) {
        await api.delete('/orders/cart/clear/');
      } else {
        localStorage.removeItem('cart');
      }
      
      dispatch({ type: CART_ACTIONS.CLEAR_CART });
    } catch (error) {
      console.error('Error clearing cart:', error);
      dispatch({ 
        type: CART_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.message || 'Failed to clear cart' 
      });
    }
  };

  // Get cart item count
  const getCartItemCount = () => {
    return state.items.reduce((total, item) => total + item.quantity, 0);
  };

  // Check if product is in cart
  const isInCart = (productId) => {
    return state.items.some(item => item.product.id === productId);
  };

  // Get cart item by product ID
  const getCartItem = (productId) => {
    return state.items.find(item => item.product.id === productId);
  };

  const value = {
    // State
    items: state.items,
    total: state.total,
    loading: state.loading,
    error: state.error,
    
    // Actions
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
    loadCartFromBackend,
    
    // Helpers
    getCartItemCount,
    isInCart,
    getCartItem,
    
    // Error handling
    clearError: () => dispatch({ type: CART_ACTIONS.CLEAR_ERROR })
  };

  return (
    <CartContext.Provider value={value}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};

export default CartContext;
