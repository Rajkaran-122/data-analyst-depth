import React, { useState, useMemo } from 'react';
import {
    BarChart, Bar, LineChart, Line, AreaChart, Area,
    PieChart, Pie, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, LineChart as LineIcon, PieChart as PieIcon, ScatterChart as ScatterIcon, TrendingUp } from 'lucide-react';

export interface VizConfig {
    type: 'bar' | 'line' | 'scatter' | 'pie' | 'area';
    xAxis: string;
    yAxis: string;
    groupBy?: string;
    title?: string;
}

interface ChartBuilderProps {
    data: { columns: { name: string; type: string }[]; rows: Record<string, any>[] };
    onSave?: (config: VizConfig) => void;
    onClose?: () => void;
}

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#14b8a6'];

const CHART_TYPES = [
    { value: 'bar', label: 'Bar Chart', icon: BarChart3 },
    { value: 'line', label: 'Line Chart', icon: LineIcon },
    { value: 'area', label: 'Area Chart', icon: TrendingUp },
    { value: 'pie', label: 'Pie Chart', icon: PieIcon },
    { value: 'scatter', label: 'Scatter Plot', icon: ScatterIcon },
] as const;

export function ChartBuilder({ data, onSave, onClose }: ChartBuilderProps) {
    const [chartType, setChartType] = useState<VizConfig['type']>('bar');
    const [xAxis, setXAxis] = useState<string>('');
    const [yAxis, setYAxis] = useState<string>('');
    const [groupBy, setGroupBy] = useState<string>('');

    // Get numeric and categorical columns
    const numericColumns = useMemo(() => {
        return data.columns.filter(col =>
            ['int', 'float', 'double', 'bigint', 'decimal', 'number'].some(type =>
                col.type.toLowerCase().includes(type)
            )
        ).map(col => col.name);
    }, [data.columns]);

    const categoricalColumns = useMemo(() => {
        return data.columns.filter(col =>
            ['string', 'varchar', 'text', 'char', 'category'].some(type =>
                col.type.toLowerCase().includes(type)
            )
        ).map(col => col.name);
    }, [data.columns]);

    const allColumns = data.columns.map(col => col.name);

    // Auto-select sensible defaults
    React.useEffect(() => {
        if (!xAxis && categoricalColumns.length > 0) {
            setXAxis(categoricalColumns[0]);
        }
        if (!yAxis && numericColumns.length > 0) {
            setYAxis(numericColumns[0]);
        }
    }, [categoricalColumns, numericColumns, xAxis, yAxis]);

    const handleSave = () => {
        if (onSave && xAxis && yAxis) {
            onSave({
                type: chartType,
                xAxis,
                yAxis,
                groupBy: groupBy || undefined,
            });
        }
    };

    const renderChart = () => {
        if (!xAxis || !yAxis || data.rows.length === 0) {
            return (
                <div className="flex items-center justify-center h-64 text-muted-foreground">
                    Select X and Y axes to preview chart
                </div>
            );
        }

        const chartData = data.rows.slice(0, 50); // Limit to 50 rows for preview

        switch (chartType) {
            case 'bar':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={xAxis} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey={yAxis} fill="#6366f1" />
                        </BarChart>
                    </ResponsiveContainer>
                );

            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={xAxis} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey={yAxis} stroke="#6366f1" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                );

            case 'area':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={xAxis} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Area type="monotone" dataKey={yAxis} stroke="#6366f1" fill="#6366f1" fillOpacity={0.6} />
                        </AreaChart>
                    </ResponsiveContainer>
                );

            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={chartData}
                                dataKey={yAxis}
                                nameKey={xAxis}
                                cx="50%"
                                cy="50%"
                                outerRadius={80}
                                label
                            >
                                {chartData.map((_, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                );

            case 'scatter':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <ScatterChart>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={xAxis} name={xAxis} />
                            <YAxis dataKey={yAxis} name={yAxis} />
                            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                            <Legend />
                            <Scatter name="Data" data={chartData} fill="#6366f1" />
                        </ScatterChart>
                    </ResponsiveContainer>
                );

            default:
                return null;
        }
    };

    return (
        <div className="flex flex-col h-full space-y-4 p-4">
            <Card>
                <CardHeader>
                    <CardTitle>Chart Configuration</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {/* Chart Type Selection */}
                    <div className="space-y-2">
                        <Label>Chart Type</Label>
                        <div className="grid grid-cols-5 gap-2">
                            {CHART_TYPES.map(({ value, label, icon: Icon }) => (
                                <Button
                                    key={value}
                                    variant={chartType === value ? 'default' : 'outline'}
                                    className="flex flex-col items-center gap-1 h-auto py-2"
                                    onClick={() => setChartType(value)}
                                >
                                    <Icon className="h-4 w-4" />
                                    <span className="text-xs">{label}</span>
                                </Button>
                            ))}
                        </div>
                    </div>

                    {/* Axis Configuration */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>X-Axis</Label>
                            <Select value={xAxis} onValueChange={setXAxis}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select column..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {allColumns.map(col => (
                                        <SelectItem key={col} value={col}>{col}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label>Y-Axis</Label>
                            <Select value={yAxis} onValueChange={setYAxis}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select column..." />
                                </SelectTrigger>
                                <SelectContent>
                                    {numericColumns.map(col => (
                                        <SelectItem key={col} value={col}>{col}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Group By (Optional) */}
                    {chartType !== 'pie' && (
                        <div className="space-y-2">
                            <Label>Group By (Optional)</Label>
                            <Select value={groupBy} onValueChange={setGroupBy}>
                                <SelectTrigger>
                                    <SelectValue placeholder="None" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="">None</SelectItem>
                                    {categoricalColumns.map(col => (
                                        <SelectItem key={col} value={col}>{col}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Live Preview */}
            <Card className="flex-1">
                <CardHeader>
                    <CardTitle>Preview</CardTitle>
                </CardHeader>
                <CardContent>
                    {renderChart()}
                    <div className="mt-4 text-sm text-muted-foreground">
                        Showing {Math.min(data.rows.length, 50)} of {data.rows.length} rows
                    </div>
                </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex justify-end gap-2">
                {onClose && (
                    <Button variant="outline" onClick={onClose}>
                        Cancel
                    </Button>
                )}
                <Button onClick={handleSave} disabled={!xAxis || !yAxis}>
                    Save Chart
                </Button>
            </div>
        </div>
    );
}
