import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, CreditCardIcon, TruckIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { useCart } from '../contexts/CartContext';
import { useAuth } from '../contexts/AuthContext';
import ShippingAddressForm from '../components/Checkout/ShippingAddressForm';
import OrderSummary from '../components/Checkout/OrderSummary';
import api from '../services/api';

const Checkout = () => {
  const navigate = useNavigate();
  const { items, total, clearCart, getCartItemCount } = useCart();
  const { isAuthenticated, user } = useAuth();
  const [currentStep, setCurrentStep] = useState(1);
  const [shippingAddress, setShippingAddress] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('cod'); // cod, card, upi
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [orderNotes, setOrderNotes] = useState('');
  const [orderEmail, setOrderEmail] = useState('');

  const itemCount = getCartItemCount();

  // Initialize email when user data is available
  useEffect(() => {
    if (user?.email) {
      setOrderEmail(user.email);
    }
  }, [user]);

  // Redirect if cart is empty or user not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/checkout');
      return;
    }
    
    if (itemCount === 0) {
      navigate('/cart');
      return;
    }
  }, [isAuthenticated, itemCount, navigate]);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  const handleAddressSelect = (address) => {
    setShippingAddress(address);
    if (currentStep === 1) {
      setCurrentStep(2);
    }
  };

  const handlePlaceOrder = async () => {
    if (!shippingAddress) {
      setError('Please select a shipping address');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const subtotal = total;
      const tax = subtotal * 0.18; // 18% GST
      const totalAmount = subtotal + tax;

      console.log('👤 User data:', user);
      console.log('📧 User email:', user?.email);
      console.log('🏠 Shipping address:', shippingAddress);
      
      const orderData = {
        shipping_address_id: shippingAddress.id,
        billing_same_as_shipping: true, // For now, assume same as shipping
        phone_number: shippingAddress.phone_number || '',
        email: orderEmail.trim(),
        notes: orderNotes || ''
      };
      
      // Validate required fields
      if (!orderData.email) {
        setError('Email address is required for order confirmation.');
        return;
      }
      
      // Validate email format
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(orderData.email)) {
        setError('Please enter a valid email address.');
        return;
      }
      
      console.log('📋 Final order data before sending:', orderData);

      console.log('🛒 Checkout: Placing order...');
      console.log('📦 Order data:', orderData);
      console.log('🌐 API URL: /orders/orders/create/');
      
      const response = await api.post('/orders/orders/create/', orderData);
      console.log('✅ Order placed successfully:', response.data);
      
      // Clear cart after successful order
      await clearCart();
      
      // Redirect to order confirmation
      navigate(`/order-confirmation/${response.data.id}`);
    } catch (error) {
      console.error('❌ Error placing order:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error data:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      
      let errorMessage = 'Failed to place order. Please try again.';
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else {
          // Handle field-specific errors
          const errors = Object.entries(error.response.data)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ');
          errorMessage = errors || errorMessage;
        }
      }
      
      console.error('❌ Final error message:', errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const steps = [
    { id: 1, name: 'Shipping', icon: TruckIcon },
    { id: 2, name: 'Payment', icon: CreditCardIcon },
    { id: 3, name: 'Review', icon: CheckCircleIcon }
  ];

  if (itemCount === 0) {
    return null; // Will redirect via useEffect
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/cart"
            className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to Cart
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <nav aria-label="Progress">
            <ol className="flex items-center">
              {steps.map((step, stepIdx) => (
                <li key={step.name} className={`${stepIdx !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''} relative`}>
                  <div className="flex items-center">
                    <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                      currentStep >= step.id
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}>
                      <step.icon className="w-5 h-5" />
                    </div>
                    <span className={`ml-4 text-sm font-medium ${
                      currentStep >= step.id ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </span>
                  </div>
                  {stepIdx !== steps.length - 1 && (
                    <div className={`absolute top-5 left-5 w-full h-0.5 ${
                      currentStep > step.id ? 'bg-blue-600' : 'bg-gray-200'
                    }`} />
                  )}
                </li>
              ))}
            </ol>
          </nav>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        <div className="lg:grid lg:grid-cols-12 lg:gap-x-8">
          {/* Main Content */}
          <div className="lg:col-span-7">
            {/* Step 1: Shipping Address */}
            {currentStep === 1 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <ShippingAddressForm
                  onAddressSelect={handleAddressSelect}
                  selectedAddressId={shippingAddress?.id}
                />
                
                {shippingAddress && (
                  <div className="mt-6 flex justify-end">
                    <button
                      onClick={() => setCurrentStep(2)}
                      className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
                    >
                      Continue to Payment
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Payment Method */}
            {currentStep === 2 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-6">Payment Method</h3>
                
                <div className="space-y-4">
                  {/* Cash on Delivery */}
                  <div className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                    paymentMethod === 'cod'
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                      : 'border-gray-200 hover:border-gray-300'
                  }`} onClick={() => setPaymentMethod('cod')}>
                    <div className="flex items-center">
                      <input
                        type="radio"
                        name="payment"
                        value="cod"
                        checked={paymentMethod === 'cod'}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <div className="ml-3">
                        <label className="text-sm font-medium text-gray-900">Cash on Delivery</label>
                        <p className="text-sm text-gray-500">Pay when your order is delivered</p>
                      </div>
                    </div>
                  </div>

                  {/* Credit/Debit Card */}
                  <div className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                    paymentMethod === 'card'
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                      : 'border-gray-200 hover:border-gray-300'
                  }`} onClick={() => setPaymentMethod('card')}>
                    <div className="flex items-center">
                      <input
                        type="radio"
                        name="payment"
                        value="card"
                        checked={paymentMethod === 'card'}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <div className="ml-3">
                        <label className="text-sm font-medium text-gray-900">Credit/Debit Card</label>
                        <p className="text-sm text-gray-500">Pay securely with your card</p>
                      </div>
                    </div>
                  </div>

                  {/* UPI */}
                  <div className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                    paymentMethod === 'upi'
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                      : 'border-gray-200 hover:border-gray-300'
                  }`} onClick={() => setPaymentMethod('upi')}>
                    <div className="flex items-center">
                      <input
                        type="radio"
                        name="payment"
                        value="upi"
                        checked={paymentMethod === 'upi'}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                      <div className="ml-3">
                        <label className="text-sm font-medium text-gray-900">UPI</label>
                        <p className="text-sm text-gray-500">Pay with Google Pay, PhonePe, Paytm</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex justify-between">
                  <button
                    onClick={() => setCurrentStep(1)}
                    className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition-colors duration-200"
                  >
                    Back to Shipping
                  </button>
                  <button
                    onClick={() => setCurrentStep(3)}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
                  >
                    Review Order
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Review Order */}
            {currentStep === 3 && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-6">Review Your Order</h3>
                
                {/* Order Notes */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Order Notes (Optional)
                  </label>
                  <textarea
                    value={orderNotes}
                    onChange={(e) => setOrderNotes(e.target.value)}
                    rows={3}
                    placeholder="Any special instructions for your order..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {/* Contact Email */}
                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact Email * <span className="text-xs text-gray-500">(for order updates)</span>
                  </label>
                  <input
                    type="email"
                    value={orderEmail}
                    onChange={(e) => setOrderEmail(e.target.value)}
                    required
                    placeholder="your.email@example.com"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    We'll send order confirmation and updates to this email address
                  </p>
                </div>

                {/* Payment Method Summary */}
                <div className="bg-gray-50 rounded-lg p-4 mb-6">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Payment Method:</h4>
                  <p className="text-sm text-gray-600">
                    {paymentMethod === 'cod' && 'Cash on Delivery'}
                    {paymentMethod === 'card' && 'Credit/Debit Card'}
                    {paymentMethod === 'upi' && 'UPI Payment'}
                  </p>
                </div>

                <div className="flex justify-between">
                  <button
                    onClick={() => setCurrentStep(2)}
                    className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-lg transition-colors duration-200"
                  >
                    Back to Payment
                  </button>
                  <button
                    onClick={handlePlaceOrder}
                    disabled={loading}
                    className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors duration-200 disabled:opacity-50"
                  >
                    {loading ? 'Placing Order...' : 'Place Order'}
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Order Summary Sidebar */}
          <div className="lg:col-span-5 mt-8 lg:mt-0">
            <OrderSummary
              shippingAddress={shippingAddress}
              showEditButton={currentStep > 1}
              onEdit={() => setCurrentStep(1)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
