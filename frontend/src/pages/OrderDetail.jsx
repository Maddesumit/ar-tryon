import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, ClockIcon, TruckIcon, CheckCircleIcon, XCircleIcon, CreditCardIcon } from '@heroicons/react/24/outline';
import api from '../services/api';

const OrderDetail = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    loadOrder();
  }, [orderId]);

  const loadOrder = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/orders/orders/${orderId}/`);
      setOrder(response.data);
    } catch (error) {
      console.error('Error loading order:', error);
      setError('Failed to load order details');
    } finally {
      setLoading(false);
    }
  };

  const cancelOrder = async () => {
    if (!window.confirm('Are you sure you want to cancel this order? This action cannot be undone.')) {
      return;
    }

    setCancelling(true);
    try {
      await api.patch(`/orders/orders/${orderId}/cancel/`);
      // Reload order to get updated status
      await loadOrder();
    } catch (error) {
      console.error('Error cancelling order:', error);
      alert(error.response?.data?.message || 'Failed to cancel order');
    } finally {
      setCancelling(false);
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      'pending': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'confirmed': 'bg-blue-100 text-blue-800 border-blue-200',
      'processing': 'bg-purple-100 text-purple-800 border-purple-200',
      'shipped': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'delivered': 'bg-green-100 text-green-800 border-green-200',
      'cancelled': 'bg-red-100 text-red-800 border-red-200'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getStatusIcon = (status) => {
    const icons = {
      'pending': ClockIcon,
      'confirmed': CheckCircleIcon,
      'processing': ClockIcon,
      'shipped': TruckIcon,
      'delivered': CheckCircleIcon,
      'cancelled': XCircleIcon
    };
    const IconComponent = icons[status] || ClockIcon;
    return <IconComponent className="h-5 w-5" />;
  };

  const getPaymentMethodLabel = (method) => {
    const labels = {
      'cod': 'Cash on Delivery',
      'card': 'Credit/Debit Card',
      'upi': 'UPI Payment'
    };
    return labels[method] || method;
  };

  const getOrderProgress = (status) => {
    const steps = ['pending', 'confirmed', 'processing', 'shipped', 'delivered'];
    const currentIndex = steps.indexOf(status);
    return currentIndex >= 0 ? currentIndex + 1 : 0;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-lg text-gray-600">Loading order details...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-16">
            <XCircleIcon className="h-16 w-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-medium text-gray-900 mb-2">Order Not Found</h2>
            <p className="text-gray-600 mb-8">{error || 'The order you are looking for does not exist.'}</p>
            <Link
              to="/orders"
              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              <ArrowLeftIcon className="h-4 w-4 mr-2" />
              Back to Orders
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const progressPercentage = (getOrderProgress(order.status) / 5) * 100;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            to="/orders"
            className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-1" />
            Back to Orders
          </Link>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Order #{order.order_number}</h1>
              <p className="text-gray-600 mt-1">Placed on {formatDate(order.created_at)}</p>
            </div>
            <div className="mt-4 sm:mt-0 flex items-center space-x-3">
              <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${getStatusColor(order.status)}`}>
                <span className="mr-2">{getStatusIcon(order.status)}</span>
                {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
              </span>
              {order.status === 'pending' && (
                <button
                  onClick={cancelOrder}
                  disabled={cancelling}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 disabled:opacity-50"
                >
                  {cancelling ? 'Cancelling...' : 'Cancel Order'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Order Progress (only for non-cancelled orders) */}
        {order.status !== 'cancelled' && (
          <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Order Progress</h2>
            <div className="relative">
              <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
                <div
                  style={{ width: `${progressPercentage}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-600 transition-all duration-300"
                />
              </div>
              <div className="flex justify-between mt-4">
                {['Pending', 'Confirmed', 'Processing', 'Shipped', 'Delivered'].map((step, index) => {
                  const isCompleted = getOrderProgress(order.status) > index;
                  const isCurrent = getOrderProgress(order.status) === index + 1;
                  return (
                    <div key={step} className="flex flex-col items-center">
                      <div className={`w-3 h-3 rounded-full ${
                        isCompleted ? 'bg-blue-600' : isCurrent ? 'bg-blue-400' : 'bg-gray-300'
                      }`} />
                      <span className={`text-xs mt-1 ${
                        isCompleted || isCurrent ? 'text-blue-600' : 'text-gray-500'
                      }`}>
                        {step}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Order Items */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-900">Order Items ({order.items.length})</h2>
              </div>
              <div className="divide-y divide-gray-200">
                {order.items.map((item) => (
                  <div key={item.id} className="p-6">
                    <div className="flex items-center space-x-4">
                      {/* Product Image */}
                      <div className="flex-shrink-0 w-20 h-20 bg-gray-200 rounded-lg overflow-hidden">
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
                      <div className="flex-grow">
                        <h3 className="text-lg font-medium text-gray-900">{item.product.name}</h3>
                        <p className="text-sm text-gray-500">
                          {typeof item.product.brand === 'object' ? item.product.brand?.name : item.product.brand}
                        </p>
                        <div className="flex space-x-4 mt-1 text-sm text-gray-600">
                          {item.selected_size && (
                            <span>Size: <strong>{item.selected_size}</strong></span>
                          )}
                          {item.selected_color && (
                            <span>Color: <strong>{item.selected_color}</strong></span>
                          )}
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          Quantity: <strong>{item.quantity}</strong>
                        </div>
                      </div>

                      {/* Price */}
                      <div className="text-right">
                        <div className="text-lg font-semibold text-gray-900">
                          {formatPrice(item.price * item.quantity)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatPrice(item.price)} each
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Order Summary & Details */}
          <div className="space-y-6">
            {/* Order Summary */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Order Summary</h2>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">{formatPrice(order.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Shipping</span>
                  <span className="text-green-600 font-medium">Free</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Tax</span>
                  <span className="font-medium">{formatPrice(order.tax)}</span>
                </div>
                <div className="border-t border-gray-200 pt-3">
                  <div className="flex justify-between">
                    <span className="text-base font-medium text-gray-900">Total</span>
                    <span className="text-xl font-semibold text-gray-900">
                      {formatPrice(order.total)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Shipping Address */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Shipping Address</h2>
              <div className="text-sm text-gray-600">
                <p className="font-medium text-gray-900">
                  {order.shipping_address.first_name} {order.shipping_address.last_name}
                </p>
                {order.shipping_address.company && (
                  <p>{order.shipping_address.company}</p>
                )}
                <p>{order.shipping_address.address_line_1}</p>
                {order.shipping_address.address_line_2 && (
                  <p>{order.shipping_address.address_line_2}</p>
                )}
                <p>
                  {order.shipping_address.city}, {order.shipping_address.state} {order.shipping_address.postal_code}
                </p>
                <p>{order.shipping_address.country}</p>
                {order.shipping_address.phone_number && (
                  <p className="mt-2">Phone: {order.shipping_address.phone_number}</p>
                )}
              </div>
            </div>

            {/* Payment Information */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Payment Information</h2>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <CreditCardIcon className="h-5 w-5" />
                <span>{getPaymentMethodLabel(order.payment_method)}</span>
              </div>
              {order.payment_method === 'cod' && (
                <p className="text-xs text-gray-500 mt-2">
                  Payment will be collected upon delivery
                </p>
              )}
            </div>

            {/* Order Notes */}
            {order.notes && (
              <div className="bg-white rounded-lg shadow-sm border p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Order Notes</h2>
                <p className="text-sm text-gray-600">{order.notes}</p>
              </div>
            )}

            {/* Additional Actions */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Need Help?</h2>
              <div className="space-y-3">
                <button className="w-full text-left px-4 py-2 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors duration-200">
                  Contact Customer Support
                </button>
                <button className="w-full text-left px-4 py-2 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors duration-200">
                  Track Package
                </button>
                {order.status === 'delivered' && (
                  <button className="w-full text-left px-4 py-2 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors duration-200">
                    Return Items
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetail;
