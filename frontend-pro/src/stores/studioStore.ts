import { create } from 'zustand';

interface StudioState {
    // Editor State
    sql: string;
    setSql: (sql: string) => void;

    // Layout State
    isSidebarOpen: boolean; // Schema browser
    toggleSidebar: () => void;

    // Selection
    activeTab: 'results' | 'visualization';
    setActiveTab: (tab: 'results' | 'visualization') => void;
}

export const useStudioStore = create<StudioState>((set) => ({
    sql: 'SELECT * FROM users LIMIT 100;',
    setSql: (sql) => set({ sql }),

    isSidebarOpen: true,
    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),

    activeTab: 'results',
    setActiveTab: (tab) => set({ activeTab: tab }),
}));
