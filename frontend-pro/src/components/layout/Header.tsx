import { useState } from 'react';
import { Bell, Search, Moon, Sun, User, LogOut } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

export function Header() {
    const { user, logout } = useAuthStore();
    const [isDark, setIsDark] = useState(true); // TODO: Context

    const toggleTheme = () => {
        const root = window.document.documentElement;
        root.classList.toggle('dark');
        setIsDark(!isDark);
    };

    return (
        <header className="h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-6 flex items-center gap-4 sticky top-0 z-10">
            {/* Search Trigger */}
            <button className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors bg-muted/50 px-3 py-1.5 rounded-md border text-sm w-64">
                <Search className="w-4 h-4" />
                <span className="flex-1 text-left">Search...</span>
                <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium opacity-100">
                    <span className="text-xs">⌘</span>K
                </kbd>
            </button>

            <div className="flex-1" />

            {/* Actions */}
            <div className="flex items-center gap-2">
                <button onClick={toggleTheme} className="p-2 hover:bg-muted rounded-full">
                    {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
                </button>
                <button className="p-2 hover:bg-muted rounded-full">
                    <Bell className="w-5 h-5" />
                </button>
            </div>

            <div className="h-6 w-px bg-border mx-2" />

            {/* Profile */}
            <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center text-sm font-medium">
                    {user?.fullName?.[0] || 'U'}
                </div>
                <button
                    onClick={logout}
                    className="text-sm font-medium hover:underline text-muted-foreground hover:text-foreground"
                >
                    Logout
                </button>
            </div>
        </header>
    );
}
