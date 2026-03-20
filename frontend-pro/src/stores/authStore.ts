import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { apiClient } from '@/lib/api';

interface User {
    id: string;
    email: string;
    fullName: string;
    isAdmin: boolean;
}

interface AuthState {
    user: User | null;
    accessToken: string | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => void;
    setUser: (user: User, token: string) => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            accessToken: null,
            isAuthenticated: false,

            login: async (email: string, password: string) => {
                try {
                    const response = await apiClient.post('/api/auth/login', { email, password });
                    const { user, access_token } = response.data;

                    set({
                        user,
                        accessToken: access_token,
                        isAuthenticated: true,
                    });

                    return true;
                } catch (error) {
                    console.error('Login failed:', error);
                    return false;
                }
            },

            logout: () => {
                set({
                    user: null,
                    accessToken: null,
                    isAuthenticated: false,
                });
            },

            setUser: (user, token) => {
                set({
                    user,
                    accessToken: token,
                    isAuthenticated: true,
                });
            },
        }),
        {
            name: 'auth-storage',
            storage: createJSONStorage(() => localStorage),
        }
    )
);
