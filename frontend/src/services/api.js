// API service for communicating with Django backend
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8001/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    console.log('🔑 API Request interceptor - Token:', token ? `${token.substring(0, 20)}...` : 'No token');
    console.log('🌐 API Request URL:', config.url);
    console.log('📤 API Request data:', config.data);
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('❌ API Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response successful:', response.status, response.config.url);
    console.log('✅ Response data:', response.data);
    return response;
  },
  (error) => {
    console.error('❌ API Response error:', error);
    console.error('❌ Error details:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method
    });
    
    if (error.response?.status === 401) {
      console.log('❌ 401 Unauthorized - removing tokens and redirecting to login');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => {
    console.log('API: Making login request to:', `${API_BASE_URL}/users/login/`);
    console.log('API: Login credentials:', credentials);
    const request = api.post('/users/login/', credentials);
    console.log('API: Login request created:', request);
    return request;
  },
  register: (userData) => api.post('/users/register/', userData),
  logout: () => api.post('/users/logout/'),
  getProfile: () => api.get('/users/profile/'),
  updateProfile: (data) => api.patch('/users/profile/', data),
};

// Products API
export const productsAPI = {
  getProducts: (params = {}) => api.get('/catalog/products/', { params }),
  getProduct: (slug) => api.get(`/catalog/products/${slug}/`),
  getCategories: () => api.get('/catalog/categories/'),
  getBrands: () => api.get('/catalog/brands/'),
  searchProducts: (query) => api.get(`/catalog/products/search/?q=${query}`),
};

// Try-on API
export const tryonAPI = {
  uploadImage: (imageFile) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    return api.post('/tryon/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getTryonResult: (id) => api.get(`/tryon/results/${id}/`),
  saveTryonResult: (data) => api.post('/tryon/save/', data),
};

export { api };
export default api;
