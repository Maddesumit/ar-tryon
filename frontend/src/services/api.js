// API service for communicating with Django backend
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

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
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/users/login/', credentials),
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
