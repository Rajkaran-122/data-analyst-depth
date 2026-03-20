import axios from 'react'; // we will install axios
import _axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

const api = _axios.create({
  baseURL: `${BACKEND_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach access token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle 401s and auto-refresh token
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Skip retry logic for login/register endpoints to avoid infinite loops
    if (originalRequest.url.includes('/auth/login') || originalRequest.url.includes('/auth/register')) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function(resolve, reject) {
          failedQueue.push({ resolve, reject });
        }).then(token => {
          originalRequest.headers['Authorization'] = 'Bearer ' + token;
          return api(originalRequest);
        }).catch(err => {
          return Promise.reject(err);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refresh_token = localStorage.getItem('refresh_token');
      
      if (!refresh_token) {
        // No refresh token means we are fully logged out
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        isRefreshing = false;
        processQueue(new Error('No refresh token'));
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const res = await _axios.post(`${BACKEND_URL}/api/auth/refresh`, { refresh_token });
        const new_access_token = res.data.access_token;
        const new_refresh_token = res.data.refresh_token;
        
        localStorage.setItem('access_token', new_access_token);
        localStorage.setItem('refresh_token', new_refresh_token);
        
        api.defaults.headers.common['Authorization'] = `Bearer ${new_access_token}`;
        originalRequest.headers['Authorization'] = `Bearer ${new_access_token}`;
        
        processQueue(null, new_access_token);
        
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed (e.g., token expired or revoked)
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        processQueue(refreshError, null);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
