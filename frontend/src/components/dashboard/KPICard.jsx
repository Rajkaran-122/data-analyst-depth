import React from 'react';
import { TrendUpIcon, TrendDownIcon, MoreIcon } from '../icons';

export function KPICard({
    title,
    value,
    change,
    changeLabel = 'vs last period',
    trend = 'neutral', // 'up' | 'down' | 'neutral'
    icon: Icon,
    delay = 0
}) {
    const trendColors = {
        up: {
            bg: 'bg-[#10B981]/10',
            text: 'text-[#10B981]',
            glow: 'hover:shadow-[0_0_40px_rgba(16,185,129,0.15)]'
        },
        down: {
            bg: 'bg-[#EF4444]/10',
            text: 'text-[#EF4444]',
            glow: 'hover:shadow-[0_0_40px_rgba(239,68,68,0.15)]'
        },
        neutral: {
            bg: 'bg-[#F59E0B]/10',
            text: 'text-[#F59E0B]',
            glow: 'hover:shadow-[0_0_40px_rgba(59,130,246,0.15)]'
        }
    };

    const colors = trendColors[trend] || trendColors.neutral;

    return (
        <div
            className={`
        relative overflow-hidden rounded-2xl
        bg-gradient-to-b from-[#1A1A24] to-[#12121A]
        border border-[#1E1E2A] hover:border-[#2A2A3A]
        p-6 transition-all duration-300
        hover:-translate-y-1 ${colors.glow}
        animate-[card-enter_0.5s_ease-out_forwards]
      `}
            style={{ animationDelay: `${delay}ms` }}
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    {Icon && (
                        <div className="p-2 rounded-lg bg-[#3B82F6]/10 text-[#3B82F6]">
                            <Icon className="w-5 h-5" />
                        </div>
                    )}
                    <span className="text-xs font-medium text-[#71717A] uppercase tracking-wider">
                        {title}
                    </span>
                </div>
                <button className="p-1 hover:bg-white/5 rounded-lg transition-colors text-[#52525B] hover:text-[#71717A]">
                    <MoreIcon className="w-5 h-5" />
                </button>
            </div>

            {/* Value */}
            <div className="mb-4">
                <span className="
          text-4xl font-bold
          bg-gradient-to-r from-white to-[#A1A1AA] bg-clip-text text-transparent
        ">
                    {value}
                </span>
            </div>

            {/* Trend Indicator */}
            <div className="flex items-center gap-2">
                <div className={`
          flex items-center gap-1 px-2 py-1 rounded-full text-sm font-medium
          ${colors.bg} ${colors.text}
        `}>
                    {trend === 'up' && <TrendUpIcon className="w-4 h-4" />}
                    {trend === 'down' && <TrendDownIcon className="w-4 h-4" />}
                    <span>{change}</span>
                </div>
                <span className="text-sm text-[#52525B]">{changeLabel}</span>
            </div>

            {/* Background Glow */}
            <div className={`
        absolute -bottom-20 -right-20 w-40 h-40 rounded-full blur-3xl opacity-20
        ${trend === 'up' ? 'bg-[#10B981]' : trend === 'down' ? 'bg-[#EF4444]' : 'bg-[#3B82F6]'}
      `} />
        </div>
    );
}

export default KPICard;
