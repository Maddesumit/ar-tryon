import React, { useState, useEffect } from 'react';
import { PlusIcon, CheckIcon } from '@heroicons/react/24/outline';
import api from '../../services/api';

const ShippingAddressForm = ({ onAddressSelect, selectedAddressId }) => {
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    company: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    phone_number: '',
    is_default: false
  });
  const [formLoading, setFormLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAddresses();
  }, []);

  const loadAddresses = async () => {
    console.log('🏠 ShippingAddress: Loading addresses...');
    try {
      setLoading(true);
      console.log('📡 Making API call to /orders/addresses/');
      const response = await api.get('/orders/addresses/');
      console.log('✅ Addresses loaded:', response.data);
      setAddresses(response.data);
      
      // Auto-select default address or first address
      if (response.data.length > 0 && !selectedAddressId) {
        const defaultAddress = response.data.find(addr => addr.is_default) || response.data[0];
        console.log('🎯 Auto-selecting address:', defaultAddress);
        onAddressSelect(defaultAddress);
      }
    } catch (error) {
      console.error('❌ Error loading addresses:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error data:', error.response?.data);
      setError('Failed to load addresses');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('💾 ShippingAddress: Saving address...');
    console.log('📋 Form data:', formData);
    
    setFormLoading(true);
    setError(null);

    try {
      // Fix field mismatch: combine first_name and last_name into name
      const requestData = {
        ...formData,
        name: `${formData.first_name} ${formData.last_name}`.trim(),
        // Remove the fields that don't exist in backend
        first_name: undefined,
        last_name: undefined
      };
      
      // Clean up undefined fields
      Object.keys(requestData).forEach(key => {
        if (requestData[key] === undefined) {
          delete requestData[key];
        }
      });
      
      console.log('📤 Request data:', requestData);
      console.log('🌐 API URL: /orders/addresses/');
      
      const response = await api.post('/orders/addresses/', requestData);
      console.log('✅ Address saved successfully:', response.data);
      
      setAddresses(prev => [...prev, response.data]);
      onAddressSelect(response.data);
      setShowForm(false);
      setFormData({
        first_name: '',
        last_name: '',
        company: '',
        address_line_1: '',
        address_line_2: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'India',
        phone_number: '',
        is_default: false
      });
    } catch (error) {
      console.error('❌ Error saving address:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error data:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      
      // More detailed error message
      let errorMessage = 'Failed to save address';
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.message) {
          errorMessage = error.response.data.message;
        } else {
          // Handle field-specific errors
          const errors = Object.entries(error.response.data)
            .map(([field, messages]) => `${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            .join('; ');
          errorMessage = errors || 'Validation error';
        }
      }
      
      console.error('❌ Final error message:', errorMessage);
      setError(errorMessage);
    } finally {
      setFormLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading addresses...</span>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Shipping Address</h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          <PlusIcon className="h-4 w-4 mr-1" />
          Add New Address
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {/* Existing Addresses */}
      {addresses.length > 0 && (
        <div className="space-y-3">
          {addresses.map((address) => (
            <div
              key={address.id}
              className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                selectedAddressId === address.id
                  ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => onAddressSelect(address)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-grow">
                  <div className="flex items-center space-x-2">
                    <h4 className="font-medium text-gray-900">
                      {address.name}
                    </h4>
                    {address.is_default && (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                        Default
                      </span>
                    )}
                  </div>
                  {address.company && (
                    <p className="text-sm text-gray-600">{address.company}</p>
                  )}
                  <p className="text-sm text-gray-600">
                    {address.address_line_1}
                    {address.address_line_2 && `, ${address.address_line_2}`}
                  </p>
                  <p className="text-sm text-gray-600">
                    {address.city}, {address.state} {address.postal_code}
                  </p>
                  <p className="text-sm text-gray-600">{address.country}</p>
                  {address.phone_number && (
                    <p className="text-sm text-gray-600">Phone: {address.phone_number}</p>
                  )}
                </div>
                {selectedAddressId === address.id && (
                  <CheckIcon className="h-5 w-5 text-blue-600" />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add New Address Form */}
      {showForm && (
        <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Add New Address</h4>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name *
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name *
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company (Optional)
              </label>
              <input
                type="text"
                name="company"
                value={formData.company}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address Line 1 *
              </label>
              <input
                type="text"
                name="address_line_1"
                value={formData.address_line_1}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address Line 2 (Optional)
              </label>
              <input
                type="text"
                name="address_line_2"
                value={formData.address_line_2}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  City *
                </label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  State *
                </label>
                <input
                  type="text"
                  name="state"
                  value={formData.state}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Postal Code * <span className="text-xs text-gray-500">(6 digits)</span>
                </label>
                <input
                  type="text"
                  name="postal_code"
                  value={formData.postal_code}
                  onChange={handleInputChange}
                  required
                  pattern="[0-9]{6}"
                  maxLength="6"
                  placeholder="123456"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number <span className="text-xs text-gray-500">(10-digit Indian mobile)</span>
              </label>
              <input
                type="tel"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleInputChange}
                pattern="[6-9][0-9]{9}"
                maxLength="10"
                placeholder="9876543210"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_default"
                checked={formData.is_default}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Set as default address
              </label>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={formLoading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200 disabled:opacity-50"
              >
                {formLoading ? 'Saving...' : 'Save Address'}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium transition-colors duration-200"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default ShippingAddressForm;
