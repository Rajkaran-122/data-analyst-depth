import React from 'react';
import { MoreIcon, RefreshIcon, ExportIcon } from '../icons';

export function ChartContainer({
    title,
    children,
    actions,
    timeRanges = ['1D', '1W', '1M', '3M', '6M', '1Y', 'ALL'],
    activeRange = '1M',
    onRangeChange,
    onRefresh,
    onExport
}) {
    return (
        <div className="
      bg-[#12121A] border border-[#1E1E2A]
      rounded-2xl overflow-hidden
    ">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-[#1E1E2A]">
                <h3 className="text-base font-semibold text-white">{title}</h3>

                <div className="flex items-center gap-2">
                    {/* Time Range Selector */}
                    {onRangeChange && (
                        <div className="flex items-center gap-1 bg-[#1A1A24] p-1 rounded-lg">
                            {timeRanges.map((range) => (
                                <button
                                    key={range}
                                    onClick={() => onRangeChange(range)}
                                    className={`
                    px-2.5 py-1 rounded-md text-xs font-medium
                    transition-all duration-150
                    ${activeRange === range
                                            ? 'bg-[#3B82F6] text-white'
                                            : 'text-[#71717A] hover:text-[#A1A1AA] hover:bg-[#22222E]'
                                        }
                  `}
                                >
                                    {range}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="flex items-center gap-1 ml-2">
                        {onRefresh && (
                            <button
                                onClick={onRefresh}
                                className="p-1.5 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24] transition-all"
                                title="Refresh"
                            >
                                <RefreshIcon className="w-4 h-4" />
                            </button>
                        )}
                        {onExport && (
                            <button
                                onClick={onExport}
                                className="p-1.5 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24] transition-all"
                                title="Export"
                            >
                                <ExportIcon className="w-4 h-4" />
                            </button>
                        )}
                        <button className="p-1.5 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24] transition-all">
                            <MoreIcon className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Chart Content */}
            <div className="p-4">
                {children}
            </div>

            {/* Optional Legend / Footer */}
            {actions && (
                <div className="px-4 pb-4 flex items-center gap-4">
                    {actions}
                </div>
            )}
        </div>
    );
}

export function ChartLegend({ items }) {
    return (
        <div className="flex items-center gap-4 flex-wrap">
            {items.map((item, index) => (
                <div key={index} className="flex items-center gap-2">
                    <span
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                    />
                    <span className="text-xs text-[#A1A1AA]">{item.label}</span>
                </div>
            ))}
        </div>
    );
}

export default ChartContainer;
