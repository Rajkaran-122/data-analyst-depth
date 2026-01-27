import React from 'react';
import {
    SearchIcon,
    NotificationIcon,
    SettingsIcon,
    UserIcon,
    RefreshIcon,
    CalendarIcon
} from '../icons';

export function TopNav({ title, subtitle, onRefresh }) {
    return (
        <header className="
      sticky top-0 z-40 h-16
      bg-[#0A0A0F]/80 backdrop-blur-xl
      border-b border-[#1E1E2A]
      flex items-center justify-between
      px-6
    ">
            {/* Left Section - Page Title */}
            <div className="flex items-center gap-4">
                <div>
                    <h1 className="text-lg font-semibold text-white">{title}</h1>
                    {subtitle && (
                        <p className="text-xs text-[#71717A]">{subtitle}</p>
                    )}
                </div>
            </div>

            {/* Center - Search */}
            <div className="flex-1 max-w-xl mx-8">
                <div className="relative">
                    <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#52525B]" />
                    <input
                        type="text"
                        placeholder="Search datasets, queries, insights..."
                        className="
              w-full h-10 pl-10 pr-4
              bg-[#12121A] border border-[#2A2A3A]
              rounded-lg text-sm text-[#A1A1AA]
              placeholder:text-[#52525B]
              focus:outline-none focus:border-[#3B82F6]
              focus:ring-1 focus:ring-[#3B82F6]/50
              transition-all duration-200
            "
                    />
                    <kbd className="
            absolute right-3 top-1/2 -translate-y-1/2
            px-2 py-0.5 text-[10px] font-mono
            bg-[#1A1A24] border border-[#2A2A3A]
            rounded text-[#52525B]
          ">
                        ⌘K
                    </kbd>
                </div>
            </div>

            {/* Right Section - Actions */}
            <div className="flex items-center gap-2">
                {/* Date Range */}
                <button className="
          flex items-center gap-2 px-3 py-2
          bg-[#12121A] border border-[#2A2A3A]
          rounded-lg text-sm text-[#A1A1AA]
          hover:bg-[#1A1A24] hover:border-[#3A3A4A]
          transition-all duration-200
        ">
                    <CalendarIcon className="w-4 h-4" />
                    <span>Last 30 Days</span>
                </button>

                {/* Refresh */}
                {onRefresh && (
                    <button
                        onClick={onRefresh}
                        className="
              p-2 rounded-lg
              text-[#71717A] hover:text-white
              hover:bg-[#1A1A24]
              transition-all duration-200
            "
                        title="Refresh data"
                    >
                        <RefreshIcon className="w-5 h-5" />
                    </button>
                )}

                {/* Notifications */}
                <button className="
          relative p-2 rounded-lg
          text-[#71717A] hover:text-white
          hover:bg-[#1A1A24]
          transition-all duration-200
        ">
                    <NotificationIcon className="w-5 h-5" />
                    <span className="
            absolute top-1.5 right-1.5 w-2 h-2
            bg-[#EF4444] rounded-full
          "/>
                </button>

                {/* Settings */}
                <button className="
          p-2 rounded-lg
          text-[#71717A] hover:text-white
          hover:bg-[#1A1A24]
          transition-all duration-200
        ">
                    <SettingsIcon className="w-5 h-5" />
                </button>

                {/* User Avatar */}
                <button className="
          flex items-center gap-2 ml-2 pl-2
          border-l border-[#2A2A3A]
        ">
                    <div className="
            w-8 h-8 rounded-full
            bg-gradient-to-br from-[#3B82F6] to-[#8B5CF6]
            flex items-center justify-center
          ">
                        <UserIcon className="w-4 h-4 text-white" />
                    </div>
                </button>
            </div>
        </header>
    );
}

export default TopNav;
