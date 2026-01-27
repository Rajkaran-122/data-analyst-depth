import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function DashboardLayout() {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    return (
        <div className="flex h-screen overflow-hidden bg-background text-foreground">
            <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} />

            <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                <Header />

                <main className="flex-1 overflow-auto p-6 scroll-smooth">
                    <Outlet />
                </main>
            </div>
        </div>
    );
}
