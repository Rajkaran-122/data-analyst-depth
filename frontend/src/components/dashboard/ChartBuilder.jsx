import React, { useState, useEffect, useMemo } from 'react';
import {
    BarChart, Bar,
    LineChart, Line,
    AreaChart, Area,
    PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { ChartContainer } from './ChartContainer';
import { RefreshIcon, DatasetIcon } from '../icons';

const COLORS = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#EC4899', '#06B6D4'];

export function ChartBuilder({ datasets = [] }) {
    const [selectedDatasetId, setSelectedDatasetId] = useState('');
    const [chartType, setChartType] = useState('bar');
    const [xAxis, setXAxis] = useState('');
    const [yAxis, setYAxis] = useState('');
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(false);

    const selectedDataset = useMemo(() =>
        datasets.find(d => d.id === selectedDatasetId),
        [datasets, selectedDatasetId]
    );

    useEffect(() => {
        if (selectedDatasetId) {
            fetchDatasetData(selectedDatasetId);
        } else {
            setChartData([]);
            setXAxis('');
            setYAxis('');
        }
    }, [selectedDatasetId]);

    const fetchDatasetData = async (id) => {
        setLoading(true);
        try {
            // Fetch preview data (first 50 rows for visualization) -> ideally fetch full column data endpoint
            const res = await fetch(`http://localhost:8000/api/datasets/${id}/preview?rows=50`);
            if (res.ok) {
                const data = await res.json();
                setChartData(data.preview || []);
                // Auto-select first suitable columns
                if (data.columns && data.columns.length > 0) {
                    const numCols = data.columns.filter(c => ['int64', 'float64', 'int', 'float'].some(t => c.dtype.includes(t)));
                    const strCols = data.columns.filter(c => !numCols.includes(c));

                    if (!xAxis && strCols.length > 0) setXAxis(strCols[0].name);
                    else if (!xAxis && data.columns.length > 0) setXAxis(data.columns[0].name);

                    if (!yAxis && numCols.length > 0) setYAxis(numCols[0].name);
                    else if (!yAxis && data.columns.length > 1) setYAxis(data.columns[1].name);
                }
            }
        } catch (error) {
            console.error("Failed to fetch dataset data", error);
        } finally {
            setLoading(false);
        }
    };

    const renderChart = () => {
        if (!chartData.length || !xAxis || !yAxis) {
            return (
                <div className="flex flex-col items-center justify-center h-64 text-[#52525B]">
                    <DatasetIcon className="w-12 h-12 mb-3 opacity-20" />
                    <p>Select a dataset and columns to visualize</p>
                </div>
            );
        }

        const CommonProps = {
            data: chartData,
            margin: { top: 10, right: 30, left: 0, bottom: 0 }
        };

        const renderAxis = () => (
            <>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2A3A" vertical={false} />
                <XAxis
                    dataKey={xAxis}
                    stroke="#71717A"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                />
                <YAxis
                    stroke="#71717A"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => value.toLocaleString()}
                />
                <Tooltip
                    contentStyle={{ backgroundColor: '#1A1A24', borderColor: '#2A2A3A', color: '#fff' }}
                    itemStyle={{ color: '#E5E7EB' }}
                />
                <Legend />
            </>
        );

        switch (chartType) {
            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart {...CommonProps}>
                            {renderAxis()}
                            <Line type="monotone" dataKey={yAxis} stroke="#3B82F6" strokeWidth={3} dot={false} activeDot={{ r: 6 }} />
                        </LineChart>
                    </ResponsiveContainer>
                );
            case 'area':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart {...CommonProps}>
                            <defs>
                                <linearGradient id="colorY" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            {renderAxis()}
                            <Area type="monotone" dataKey={yAxis} stroke="#8B5CF6" fillOpacity={1} fill="url(#colorY)" />
                        </AreaChart>
                    </ResponsiveContainer>
                );
            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey={yAxis}
                                nameKey={xAxis}
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1A1A24', borderColor: '#2A2A3A', color: '#fff' }}
                                itemStyle={{ color: '#E5E7EB' }}
                            />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );
            case 'bar':
            default:
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart {...CommonProps}>
                            {renderAxis()}
                            <Bar dataKey={yAxis} fill="#3B82F6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                );
        }
    };

    return (
        <ChartContainer
            title="Chart Builder"
            actions={
                <div className="flex gap-4 w-full">
                    {/* Dataset Selector */}
                    <div className="flex-1 min-w-[200px]">
                        <label className="text-xs text-[#71717A] block mb-1">Dataset</label>
                        <select
                            className="w-full bg-[#1A1A24] border border-[#2A2A3A] text-white text-sm rounded-lg px-3 py-2 focus:border-[#3B82F6] outline-none"
                            value={selectedDatasetId}
                            onChange={(e) => setSelectedDatasetId(e.target.value)}
                        >
                            <option value="">Select Dataset...</option>
                            {datasets.map(ds => (
                                <option key={ds.id} value={ds.id}>{ds.name}</option>
                            ))}
                        </select>
                    </div>

                    {/* Chart Type Selector */}
                    <div className="w-[150px]">
                        <label className="text-xs text-[#71717A] block mb-1">Chart Type</label>
                        <select
                            className="w-full bg-[#1A1A24] border border-[#2A2A3A] text-white text-sm rounded-lg px-3 py-2 focus:border-[#3B82F6] outline-none"
                            value={chartType}
                            onChange={(e) => setChartType(e.target.value)}
                        >
                            <option value="bar">Bar Chart</option>
                            <option value="line">Line Chart</option>
                            <option value="area">Area Chart</option>
                            <option value="pie">Pie Chart</option>
                        </select>
                    </div>
                </div>
            }
        >
            <div className="space-y-4">
                {/* Column Selectors - Only show if dataset selected */}
                {selectedDataset && (
                    <div className="flex gap-4 mb-4 p-3 bg-[#1A1A24]/50 rounded-xl border border-[#2A2A3A]/50">
                        <div className="flex-1">
                            <label className="text-xs text-[#71717A] block mb-1">X Axis (Category)</label>
                            <select
                                className="w-full bg-[#12121A] border border-[#2A2A3A] text-white text-sm rounded-lg px-3 py-2 focus:border-[#3B82F6] outline-none"
                                value={xAxis}
                                onChange={(e) => setXAxis(e.target.value)}
                            >
                                <option value="">Select Column...</option>
                                {selectedDataset.columns?.map(col => (
                                    <option key={col.name} value={col.name}>{col.name} ({col.dtype})</option>
                                ))}
                            </select>
                        </div>
                        <div className="flex-1">
                            <label className="text-xs text-[#71717A] block mb-1">Y Axis (Value)</label>
                            <select
                                className="w-full bg-[#12121A] border border-[#2A2A3A] text-white text-sm rounded-lg px-3 py-2 focus:border-[#3B82F6] outline-none"
                                value={yAxis}
                                onChange={(e) => setYAxis(e.target.value)}
                            >
                                <option value="">Select Column...</option>
                                {selectedDataset.columns?.map(col => (
                                    <option key={col.name} value={col.name}>{col.name} ({col.dtype})</option>
                                ))}
                            </select>
                        </div>
                        <button
                            onClick={() => fetchDatasetData(selectedDatasetId)}
                            className="mt-5 p-2 rounded-lg bg-[#2A2A3A] hover:bg-[#3B82F6] text-white transition-colors"
                            title="Refresh Data"
                        >
                            <RefreshIcon className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                )}

                {/* Chart Render Area */}
                <div className="min-h-[300px] w-full">
                    {loading ? (
                        <div className="flex items-center justify-center h-[300px]">
                            <div className="w-8 h-8 border-4 border-[#3B82F6] border-t-transparent rounded-full animate-spin"></div>
                        </div>
                    ) : (
                        renderChart()
                    )}
                </div>
            </div>
        </ChartContainer>
    );
}

export default ChartBuilder;
