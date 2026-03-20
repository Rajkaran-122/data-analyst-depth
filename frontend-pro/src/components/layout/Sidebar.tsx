import { NavLink } from 'react-router-dom';
import {
    LayoutDashboard,
    Database,
    Code2,
    Settings,
    History,
    FolderKanban,
    ChevronLeft
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/authStore';

interface SidebarProps {
    collapsed: boolean;
    setCollapsed: (v: boolean) => void;
}

export function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
    const { user } = useAuthStore();

    const navItems = [
        { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/studio', icon: Code2, label: 'Data Studio' },
        { to: '/datasets', icon: Database, label: 'Datasets' },
        { to: '/workspaces', icon: FolderKanban, label: 'Workspaces' },
        { to: '/history', icon: History, label: 'History' },
        { to: '/settings', icon: Settings, label: 'Settings' },
    ];

    return (
        <div className={cn(
            "h-screen border-r bg-card transition-all duration-300 flex flex-col z-20",
            collapsed ? "w-16" : "w-64"
        )}>
            {/* Brand */}
            <div className="h-14 border-b flex items-center px-3.5 gap-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center shrink-0">
                    <Code2 className="w-5 h-5 text-primary-foreground" />
                </div>
                {!collapsed && (
                    <span className="font-bold text-lg tracking-tight">DataPortal</span>
                )}
            </div>

            {/* Nav */}
            <nav className="flex-1 p-3 space-y-1">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) => cn(
                            "flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm font-medium",
                            "hover:bg-muted/80 text-muted-foreground hover:text-foreground",
                            isActive && "bg-primary/10 text-primary hover:bg-primary/15",
                            collapsed && "justify-center px-0"
                        )}
                    >
                        <item.icon className="w-5 h-5 shrink-0" />
                        {!collapsed && <span>{item.label}</span>}
                    </NavLink>
                ))}
            </nav>

            {/* Footer / Toggle */}
            <div className="p-3 border-t">
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-muted-foreground hover:text-foreground rounded-md hover:bg-muted/80 transition-colors"
                >
                    <ChevronLeft className={cn("w-5 h-5 transition-transform", collapsed && "rotate-180")} />
                    {!collapsed && <span>Collapse</span>}
                </button>
            </div>
        </div>
    );
}
