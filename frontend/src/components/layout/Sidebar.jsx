import React, { useState } from 'react';
import {
    DashboardIcon,
    DatasetIcon,
    ExplorerIcon,
    AnalyticsIcon,
    AIAssistantIcon,
    ReportsIcon,
    SettingsIcon,
    ChevronLeftIcon,
    DocumentIcon,
    PlusIcon
} from '../icons';

const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: DashboardIcon },
    { id: 'datasets', label: 'Datasets', icon: DatasetIcon },
    { id: 'explorer', label: 'Data Explorer', icon: ExplorerIcon },
    { id: 'analytics', label: 'Analytics', icon: AnalyticsIcon },
    { id: 'ai-chat', label: 'AI Assistant', icon: AIAssistantIcon },
    { id: 'reports', label: 'Reports', icon: ReportsIcon },
];

const workspaces = [
    { id: 'sales', name: 'Sales Analytics', color: '#3B82F6' },
    { id: 'marketing', name: 'Marketing', color: '#8B5CF6' },
    { id: 'finance', name: 'Financial', color: '#10B981' },
];

export function Sidebar({ activeTab, onTabChange, collapsed, onToggleCollapse }) {
    const [activeWorkspace, setActiveWorkspace] = useState('sales');

    return (
        <aside
            className={`
        fixed left-0 top-0 h-screen z-50
        bg-[#12121A] border-r border-[#1E1E2A]
        flex flex-col transition-all duration-300 ease-in-out
        ${collapsed ? 'w-[72px]' : 'w-[260px]'}
      `}
        >
            {/* Logo */}
            <div className={`
        flex items-center gap-3 px-4 h-16 border-b border-[#1E1E2A]
        ${collapsed ? 'justify-center' : ''}
      `}>
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#3B82F6] to-[#8B5CF6] flex items-center justify-center">
                    <span className="text-white font-bold text-sm">DA</span>
                </div>
                {!collapsed && (
                    <div className="flex flex-col">
                        <span className="text-sm font-semibold text-white">Data Analyst</span>
                        <span className="text-xs text-[#71717A]">Depth Portal</span>
                    </div>
                )}
            </div>

            {/* Main Navigation */}
            <div className="flex-1 overflow-y-auto py-4">
                {!collapsed && (
                    <div className="px-4 mb-2">
                        <span className="text-[10px] font-semibold text-[#52525B] uppercase tracking-wider">
                            Main Menu
                        </span>
                    </div>
                )}

                <nav className="space-y-1 px-3">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = activeTab === item.id;

                        return (
                            <button
                                key={item.id}
                                onClick={() => onTabChange(item.id)}
                                className={`
                  w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                  transition-all duration-200 group
                  ${collapsed ? 'justify-center' : ''}
                  ${isActive
                                        ? 'bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white shadow-lg shadow-blue-500/25'
                                        : 'text-[#A1A1AA] hover:bg-[#22222E] hover:text-white'
                                    }
                `}
                                title={collapsed ? item.label : undefined}
                            >
                                <Icon className="w-5 h-5 flex-shrink-0" />
                                {!collapsed && (
                                    <span className="text-sm font-medium">{item.label}</span>
                                )}
                            </button>
                        );
                    })}
                </nav>

                {/* Workspaces Section */}
                {!collapsed && (
                    <div className="mt-6 px-3">
                        <div className="px-1 mb-2 flex items-center justify-between">
                            <span className="text-[10px] font-semibold text-[#52525B] uppercase tracking-wider">
                                Workspaces
                            </span>
                        </div>

                        <div className="space-y-1">
                            {workspaces.map((ws) => (
                                <button
                                    key={ws.id}
                                    onClick={() => setActiveWorkspace(ws.id)}
                                    className={`
                    w-full flex items-center gap-3 px-3 py-2 rounded-lg
                    text-sm transition-all duration-200
                    ${activeWorkspace === ws.id
                                            ? 'bg-[#1A1A24] text-white'
                                            : 'text-[#71717A] hover:bg-[#1A1A24] hover:text-[#A1A1AA]'
                                        }
                  `}
                                >
                                    <span
                                        className="w-2 h-2 rounded-full flex-shrink-0"
                                        style={{ backgroundColor: ws.color }}
                                    />
                                    <span className="truncate">{ws.name}</span>
                                </button>
                            ))}

                            <button className="
                w-full flex items-center gap-3 px-3 py-2 rounded-lg
                text-sm text-[#52525B] hover:text-[#71717A] hover:bg-[#1A1A24]
                transition-all duration-200
              ">
                                <PlusIcon className="w-4 h-4" />
                                <span>Create Workspace</span>
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Bottom Section */}
            <div className="border-t border-[#1E1E2A] py-3 px-3 space-y-1">
                <button
                    onClick={() => onTabChange('settings')}
                    className={`
            w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
            text-[#A1A1AA] hover:bg-[#22222E] hover:text-white
            transition-all duration-200
            ${collapsed ? 'justify-center' : ''}
          `}
                    title={collapsed ? 'Settings' : undefined}
                >
                    <SettingsIcon className="w-5 h-5 flex-shrink-0" />
                    {!collapsed && <span className="text-sm font-medium">Settings</span>}
                </button>

                <button
                    onClick={() => onTabChange('docs')}
                    className={`
            w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
            text-[#A1A1AA] hover:bg-[#22222E] hover:text-white
            transition-all duration-200
            ${collapsed ? 'justify-center' : ''}
          `}
                    title={collapsed ? 'Documentation' : undefined}
                >
                    <DocumentIcon className="w-5 h-5 flex-shrink-0" />
                    {!collapsed && <span className="text-sm font-medium">Documentation</span>}
                </button>

                {/* Collapse Toggle */}
                <button
                    onClick={onToggleCollapse}
                    className={`
            w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
            text-[#52525B] hover:bg-[#22222E] hover:text-[#71717A]
            transition-all duration-200
            ${collapsed ? 'justify-center' : ''}
          `}
                >
                    <ChevronLeftIcon
                        className={`w-5 h-5 flex-shrink-0 transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`}
                    />
                    {!collapsed && <span className="text-sm">Collapse</span>}
                </button>
            </div>
        </aside>
    );
}

export default Sidebar;
