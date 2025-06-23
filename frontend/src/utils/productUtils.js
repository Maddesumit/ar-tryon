// Utility functions for product data handling

/**
 * Safely get the brand name from a brand object or string
 * @param {string|object} brand - Brand data (string or object with name property)
 * @returns {string} Brand name or empty string if not available
 */
export const getBrandName = (brand) => {
  if (!brand) return '';
  if (typeof brand === 'string') return brand;
  if (typeof brand === 'object' && brand.name) return brand.name;
  return '';
};

/**
 * Safely get the category name from a category object or string
 * @param {string|object} category - Category data (string or object with name property)
 * @returns {string} Category name or empty string if not available
 */
export const getCategoryName = (category) => {
  if (!category) return '';
  if (typeof category === 'string') return category;
  if (typeof category === 'object' && category.name) return category.name;
  return '';
};

/**
 * Format price in Indian Rupees
 * @param {number|string} price - Price value
 * @returns {string} Formatted price string
 */
export const formatPrice = (price) => {
  const numPrice = parseFloat(price) || 0;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(numPrice);
};

/**
 * Format date in Indian locale
 * @param {string|Date} date - Date to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export const formatDate = (date, options = {}) => {
  const defaultOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    ...options
  };
  
  return new Date(date).toLocaleDateString('en-IN', defaultOptions);
};

/**
 * Safely get product image URL
 * @param {object} product - Product object
 * @param {number} index - Image index (default: 0)
 * @returns {string} Image URL or placeholder
 */
export const getProductImageUrl = (product, index = 0) => {
  if (product?.images && product.images.length > index) {
    return product.images[index].image || product.images[index].url;
  }
  return 'https://via.placeholder.com/300x400?text=No+Image';
};

/**
 * Calculate discount percentage
 * @param {number} originalPrice - Original price
 * @param {number} salePrice - Sale price
 * @returns {number} Discount percentage
 */
export const calculateDiscountPercentage = (originalPrice, salePrice) => {
  if (!originalPrice || !salePrice || salePrice >= originalPrice) return 0;
  return Math.round(((originalPrice - salePrice) / originalPrice) * 100);
};

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};

/**
 * Generate order status color classes
 * @param {string} status - Order status
 * @returns {string} CSS classes for status styling
 */
export const getStatusColorClasses = (status) => {
  const statusColors = {
    'pending': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'confirmed': 'bg-blue-100 text-blue-800 border-blue-200',
    'processing': 'bg-purple-100 text-purple-800 border-purple-200',
    'shipped': 'bg-indigo-100 text-indigo-800 border-indigo-200',
    'delivered': 'bg-green-100 text-green-800 border-green-200',
    'cancelled': 'bg-red-100 text-red-800 border-red-200'
  };
  return statusColors[status] || 'bg-gray-100 text-gray-800 border-gray-200';
};
