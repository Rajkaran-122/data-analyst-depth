import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request Interceptor: Attach Token
apiClient.interceptors.request.use((config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
        config.headers.Authorization = `Bearer ${token}`; // V2: Fixed spacing
    }
    return config;
});

// Response Interceptor: Handle Refresh
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise(function (resolve, reject) {
                    failedQueue.push({ resolve, reject });
                })
                    .then((token) => {
                        originalRequest.headers['Authorization'] = 'Bearer ' + token;
                        return apiClient(originalRequest);
                    })
                    .catch((err) => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // In a real app, you'd have a separate refresh token likely in httpOnly cookie
                // or stored in local storage. Here we assume the backend handles refresh logic via cookie
                // OR we need to send a refresh token if we stored it.
                // For this demo, let's assume we post to /refresh.

                // NOTE: The previous BRD implementation used local storage for refresh token.
                // We should really store it. 
                // For simplicity in this "Foundation" phase, we'll just redirect to login if 401.
                // Implementing full refresh rotation requires storing the refresh token too.

                // Mock refresh for now to avoid infinite loops if backend is strict
                throw new Error("Session expired");

            } catch (err) {
                processQueue(err, null);
                useAuthStore.getState().logout();
                window.location.href = '/login'; // Force redirect
                return Promise.reject(err);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);
