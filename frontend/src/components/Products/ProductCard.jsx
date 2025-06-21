import React from 'react';
import { Link } from 'react-router-dom';
import { StarIcon, HeartIcon, EyeIcon } from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';

const ProductCard = ({ product }) => {
  const {
    id,
    slug,
    name,
    price,
    images = [],
    brand,
    category,
    average_rating = 0,
    review_count = 0,
    ar_enabled = false
  } = product;

  // Get the first image or use a placeholder
  const imageUrl = images.length > 0 
    ? images[0].image || images[0].url 
    : 'https://via.placeholder.com/300x400?text=No+Image';

  // Format price
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(price);
  };

  // Render star rating
  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <StarIconSolid key={i} className="h-4 w-4 text-yellow-400" />
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <StarIcon className="h-4 w-4 text-gray-300" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <StarIconSolid className="h-4 w-4 text-yellow-400" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <StarIcon key={i} className="h-4 w-4 text-gray-300" />
        );
      }
    }
    return stars;
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden group hover:shadow-lg dark:hover:shadow-xl transition-all duration-300">
      {/* Product Image */}
      <div className="relative">
        <Link to={`/products/${slug}`}>
          <img
            src={imageUrl}
            alt={name}
            className="w-full h-48 sm:h-64 object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/300x400?text=No+Image';
            }}
          />
        </Link>
        
        {/* AR Badge */}
        {ar_enabled && (
          <div className="absolute top-2 left-2 bg-purple-600 dark:bg-purple-700 text-white px-2 py-1 rounded-full text-xs font-medium flex items-center">
            <EyeIcon className="h-3 w-3 mr-1" />
            AR
          </div>
        )}

        {/* Wishlist Button */}
        <button className="absolute top-2 right-2 p-2 bg-white dark:bg-gray-700 rounded-full shadow-md hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
          <HeartIcon className="h-5 w-5 text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400" />
        </button>

        {/* Quick Actions on Hover */}
        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/50 to-transparent p-4 transform translate-y-full group-hover:translate-y-0 transition-transform duration-300">
          <div className="flex gap-2">
            <Link
              to={`/products/${slug}`}
              className="flex-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 rounded text-sm font-medium text-center hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              View Details
            </Link>
            {ar_enabled && (
              <Link
                to={`/try-on?product=${id}`}
                className="flex-1 bg-purple-600 dark:bg-purple-700 text-white px-3 py-2 rounded text-sm font-medium text-center hover:bg-purple-700 dark:hover:bg-purple-600 transition-colors flex items-center justify-center"
              >
                <EyeIcon className="h-4 w-4 mr-1" />
                Try On
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Product Info */}
      <div className="p-4">
        {/* Brand */}
        {brand && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{brand.name || brand}</p>
        )}

        {/* Product Name */}
        <Link to={`/products/${slug}`}>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2 hover:text-purple-600 dark:hover:text-purple-400 transition-colors line-clamp-2">
            {name}
          </h3>
        </Link>

        {/* Category */}
        {category && (
          <p className="text-xs text-gray-400 mb-2">{category.name || category}</p>
        )}

        {/* Rating */}
        {review_count > 0 && (
          <div className="flex items-center mb-2">
            <div className="flex items-center">
              {renderStars(average_rating)}
            </div>
            <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
              ({review_count})
            </span>
          </div>
        )}

        {/* Price */}
        <div className="flex items-center justify-between">
          <span className="text-lg font-bold text-gray-900 dark:text-white">
            {formatPrice(price)}
          </span>
          
          {/* AR Quick Try */}
          {ar_enabled && (
            <Link
              to={`/try-on?product=${id}`}
              className="text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 text-sm font-medium flex items-center"
            >
              <EyeIcon className="h-4 w-4 mr-1" />
              Try AR
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
