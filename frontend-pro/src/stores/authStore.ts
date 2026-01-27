import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface User {
    id: string;
    email: string;
    full_name: string;
    avatar_url?: string;
    is_superuser: boolean;
}

interface AuthState {
    user: User | null;
    accessToken: string | null;
    isAuthenticated: boolean;

    // Actions
    setAuth: (user: User, accessToken: string) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            accessToken: null,
            isAuthenticated: false,

            setAuth: (user, accessToken) => set({ user, accessToken, isAuthenticated: true }),
            logout: () => set({ user: null, accessToken: null, isAuthenticated: false }),
        }),
        {
            name: 'auth-storage',
            storage: createJSONStorage(() => localStorage),
        }
    )
);
