import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  CameraIcon, 
  PhotoIcon, 
  ArrowPathIcon,
  EyeIcon,
  ShareIcon,
  HeartIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { api } from '../services/api';

const TryOn = () => {
  const [searchParams] = useSearchParams();
  const productId = searchParams.get('product');
  
  const [product, setProduct] = useState(null);
  const [userImage, setUserImage] = useState(null);
  const [userImagePreview, setUserImagePreview] = useState(null);
  const [tryOnResult, setTryOnResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedProductImage, setSelectedProductImage] = useState(0);
  
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [cameraStream, setCameraStream] = useState(null);
  const [showCamera, setShowCamera] = useState(false);

  useEffect(() => {
    if (productId) {
      fetchProduct();
    }
  }, [productId]);

  const fetchProduct = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/catalog/products/${productId}/`);
      setProduct(response.data);
    } catch (error) {
      console.error('Error fetching product:', error);
      setError('Product not found');
    } finally {
      setLoading(false);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraStream(stream);
        setShowCamera(true);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      setError('Could not access camera. Please check permissions.');
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    setShowCamera(false);
  };

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      canvas.toBlob((blob) => {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        setUserImage(file);
        setUserImagePreview(URL.createObjectURL(blob));
        stopCamera();
      }, 'image/jpeg', 0.8);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUserImage(file);
      setUserImagePreview(URL.createObjectURL(file));
    }
  };

  const processTryOn = async () => {
    if (!userImage || !product) {
      setError('Please select both a user image and a product');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('user_image', userImage);
      formData.append('product_id', product.id);
      formData.append('product_image_index', selectedProductImage);

      const response = await api.post('/tryon/process/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setTryOnResult(response.data);
    } catch (error) {
      console.error('Error processing try-on:', error);
      setError('Failed to process try-on. Please try again.');
    } finally {
      setProcessing(false);
    }
  };

  const clearUserImage = () => {
    setUserImage(null);
    setUserImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const shareResult = async () => {
    if (tryOnResult && navigator.share) {
      try {
        await navigator.share({
          title: 'My AR Try-On Result',
          text: `Check out how I look in ${product.name}!`,
          url: window.location.href
        });
      } catch (error) {
        console.error('Error sharing:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="bg-gray-300 h-8 rounded mb-4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-gray-300 h-96 rounded-lg"></div>
            <div className="bg-gray-300 h-96 rounded-lg"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Virtual Try-On</h1>
        <p className="text-gray-600">
          Upload your photo or take a picture to see how you look in our products
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Product Selection */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Select Product</h2>
            
            {product ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <img
                    src={product.images?.[0]?.image || product.images?.[0]?.url || 'https://via.placeholder.com/100x100?text=No+Image'}
                    alt={product.name}
                    className="w-16 h-16 object-cover rounded-lg"
                  />
                  <div>
                    <h3 className="font-medium">{product.name}</h3>
                    <p className="text-gray-600">{product.brand?.name}</p>
                    <p className="font-semibold">
                      {new Intl.NumberFormat('en-IN', {
                        style: 'currency',
                        currency: 'INR'
                      }).format(product.price)}
                    </p>
                  </div>
                </div>

                {/* Product Images Selection */}
                {product.images && product.images.length > 1 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Choose product angle:
                    </label>
                    <div className="flex space-x-2 overflow-x-auto">
                      {product.images.map((image, index) => (
                        <button
                          key={index}
                          onClick={() => setSelectedProductImage(index)}
                          className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 ${
                            selectedProductImage === index 
                              ? 'border-purple-600' 
                              : 'border-gray-200'
                          }`}
                        >
                          <img
                            src={image.image || image.url}
                            alt={`${product.name} ${index + 1}`}
                            className="w-full h-full object-cover"
                          />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600">No product selected</p>
                <a
                  href="/products"
                  className="mt-2 text-purple-600 hover:text-purple-700 font-medium"
                >
                  Browse Products
                </a>
              </div>
            )}
          </div>

          {/* User Image Upload */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Your Photo</h2>
            
            {userImagePreview ? (
              <div className="relative">
                <img
                  src={userImagePreview}
                  alt="User upload"
                  className="w-full h-64 object-cover rounded-lg"
                />
                <button
                  onClick={clearUserImage}
                  className="absolute top-2 right-2 bg-white p-1 rounded-full shadow-md hover:bg-gray-50"
                >
                  <XMarkIcon className="h-5 w-5 text-gray-600" />
                </button>
              </div>
            ) : (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <div className="space-y-4">
                  <div className="flex justify-center">
                    <PhotoIcon className="h-12 w-12 text-gray-400" />
                  </div>
                  <div>
                    <p className="text-gray-600 mb-4">
                      Upload a photo or take a picture to get started
                    </p>
                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                      >
                        <PhotoIcon className="h-5 w-5 mr-2" />
                        Upload Photo
                      </button>
                      <button
                        onClick={startCamera}
                        className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                      >
                        <CameraIcon className="h-5 w-5 mr-2" />
                        Take Photo
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="sr-only"
            />
          </div>

          {/* Camera Modal */}
          {showCamera && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Take a Photo</h3>
                  <button
                    onClick={stopCamera}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>
                <div className="space-y-4">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    className="w-full rounded-lg"
                  />
                  <button
                    onClick={capturePhoto}
                    className="w-full bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700"
                  >
                    Capture Photo
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Try-On Button */}
          {userImage && product && (
            <button
              onClick={processTryOn}
              disabled={processing}
              className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {processing ? (
                <>
                  <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <EyeIcon className="h-5 w-5 mr-2" />
                  Try On
                </>
              )}
            </button>
          )}
        </div>

        {/* Right Column - Results */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Try-On Result</h2>
          
          {tryOnResult ? (
            <div className="space-y-4">
              <img
                src={tryOnResult.result_image}
                alt="Try-on result"
                className="w-full h-96 object-cover rounded-lg"
              />
              
              <div className="flex space-x-3">
                <button
                  onClick={shareResult}
                  className="flex-1 border border-gray-300 px-4 py-2 rounded-md hover:bg-gray-50 flex items-center justify-center"
                >
                  <ShareIcon className="h-5 w-5 mr-2" />
                  Share
                </button>
                <button className="flex-1 border border-gray-300 px-4 py-2 rounded-md hover:bg-gray-50 flex items-center justify-center">
                  <HeartIcon className="h-5 w-5 mr-2" />
                  Save
                </button>
              </div>

              {tryOnResult.confidence && (
                <div className="text-sm text-gray-600">
                  Confidence: {Math.round(tryOnResult.confidence * 100)}%
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <EyeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">
                {processing ? 'Processing your try-on...' : 'Your try-on result will appear here'}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Hidden canvas for photo capture */}
      <canvas ref={canvasRef} className="sr-only" />
    </div>
  );
};

export default TryOn;
