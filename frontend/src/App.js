import React, { useState, useCallback, useEffect, useMemo } from 'react';
import '@/App.css';

// Layout Components
import { Sidebar } from '@/components/layout/Sidebar';
import { TopNav } from '@/components/layout/TopNav';

// Dashboard Components
import { KPICard } from '@/components/dashboard/KPICard';
import { ChartContainer, ChartLegend } from '@/components/dashboard/ChartContainer';

// AI Components
import { ChatInterface } from '@/components/ai/ChatInterface';

// Icons
import {
  AnalyticsIcon,
  DatasetIcon,
  ExplorerIcon,
  AIAssistantIcon,
  UploadIcon,
  DocumentIcon,
  RefreshIcon,
  PlusIcon,
  SearchIcon
} from '@/components/icons';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// ============================================================================
// Dashboard Page - Now fetches live data
// ============================================================================
function DashboardPage() {
  const [kpiData, setKpiData] = useState([]);
  const [activity, setActivity] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [sourceData, setSourceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [chartRange, setChartRange] = useState('1M');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsRes, activityRes, chartsRes, sourcesRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/stats`),
        fetch(`${API_BASE}/dashboard/activity?limit=5`),
        fetch(`${API_BASE}/dashboard/charts/queries?range=${chartRange}`),
        fetch(`${API_BASE}/dashboard/charts/sources`)
      ]);

      if (statsRes.ok) {
        const stats = await statsRes.json();
        const iconMap = {
          analytics: AnalyticsIcon,
          dataset: DatasetIcon,
          explorer: ExplorerIcon,
          document: DocumentIcon
        };
        setKpiData(stats.kpis.map(kpi => ({
          ...kpi,
          icon: iconMap[kpi.icon] || AnalyticsIcon
        })));
      }

      if (activityRes.ok) {
        const activityData = await activityRes.json();
        setActivity(activityData.activity || []);
      }

      if (chartsRes.ok) {
        const charts = await chartsRes.json();
        setChartData(charts.data || []);
      }

      if (sourcesRes.ok) {
        const sources = await sourcesRes.json();
        setSourceData(sources.data || []);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
      // Use fallback data
      setKpiData([
        { id: 'queries', title: 'Total Queries', value: '0', change: '+0%', trend: 'up', icon: AnalyticsIcon },
        { id: 'datasets', title: 'Datasets', value: '0', change: '+0%', trend: 'up', icon: DatasetIcon },
        { id: 'insights', title: 'Insights Generated', value: '0', change: '+0%', trend: 'up', icon: ExplorerIcon },
        { id: 'reports', title: 'Reports', value: '0', change: '0%', trend: 'neutral', icon: DocumentIcon },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRangeChange = async (range) => {
    setChartRange(range);
    try {
      const res = await fetch(`${API_BASE}/dashboard/charts/queries?range=${range}`);
      if (res.ok) {
        const data = await res.json();
        setChartData(data.data || []);
      }
    } catch (error) {
      console.error('Failed to fetch chart data:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {(loading ? Array(4).fill({}) : kpiData).map((kpi, index) => (
          <KPICard
            key={kpi.id || index}
            title={kpi.title || 'Loading...'}
            value={kpi.value || '--'}
            change={kpi.change || '0%'}
            trend={kpi.trend || 'neutral'}
            icon={kpi.icon}
            delay={index * 100}
          />
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Chart */}
        <div className="lg:col-span-2">
          <ChartContainer
            title="Query Trends"
            onRangeChange={handleRangeChange}
            activeRange={chartRange}
            onRefresh={fetchDashboardData}
          >
            <div className="h-64 flex items-end justify-between gap-1 px-2">
              {chartData.length > 0 ? (
                chartData.slice(-30).map((point, i) => {
                  const maxVal = Math.max(...chartData.map(d => d.queries || 0));
                  const height = maxVal > 0 ? ((point.queries || 0) / maxVal) * 100 : 10;
                  return (
                    <div
                      key={i}
                      className="flex-1 bg-gradient-to-t from-[#3B82F6] to-[#8B5CF6] rounded-t-sm transition-all hover:opacity-80"
                      style={{ height: `${Math.max(height, 5)}%` }}
                      title={`${point.date}: ${point.queries} queries`}
                    />
                  );
                })
              ) : (
                <div className="w-full h-full flex items-center justify-center text-[#52525B]">
                  <div className="text-center">
                    <AnalyticsIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p className="text-sm">No chart data available</p>
                  </div>
                </div>
              )}
            </div>
          </ChartContainer>
        </div>

        {/* Side Chart - Pie/Doughnut */}
        <div>
          <ChartContainer title="Data Sources">
            <div className="h-64 flex flex-col items-center justify-center">
              {sourceData.length > 0 ? (
                <>
                  <div className="flex flex-wrap gap-3 justify-center">
                    {sourceData.map((source, i) => (
                      <div key={i} className="flex items-center gap-2">
                        <span
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: source.color }}
                        />
                        <span className="text-xs text-[#A1A1AA]">
                          {source.name} ({source.percentage || source.value}%)
                        </span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="text-center text-[#52525B]">
                  <DatasetIcon className="w-10 h-10 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">No datasets yet</p>
                </div>
              )}
            </div>
          </ChartContainer>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-white">Recent Activity</h3>
          <button
            onClick={fetchDashboardData}
            className="p-1.5 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24] transition-all"
          >
            <RefreshIcon className="w-4 h-4" />
          </button>
        </div>
        <div className="space-y-3">
          {activity.length > 0 ? (
            activity.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-4 p-3 rounded-lg bg-[#1A1A24] border border-[#1E1E2A]"
              >
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${item.color}20` }}
                >
                  <DocumentIcon className="w-5 h-5" style={{ color: item.color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{item.title}</p>
                  <p className="text-xs text-[#71717A]">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${item.status === 'success' || item.status === 'completed' || item.status === 'ready'
                    ? 'bg-[#10B981]/10 text-[#10B981]'
                    : 'bg-[#EF4444]/10 text-[#EF4444]'
                  }`}>
                  {item.status}
                </span>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-[#52525B]">
              <p className="text-sm">No recent activity</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Datasets Page - Full implementation with API integration
// ============================================================================
function DatasetsPage() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const res = await fetch(`${API_BASE}/datasets`);
      if (res.ok) {
        const data = await res.json();
        setDatasets(data.datasets || []);
      }
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/datasets`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        fetchDatasets();
      }
    } catch (error) {
      console.error('Failed to upload dataset:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/datasets/${id}`, { method: 'DELETE' });
      if (res.ok) {
        fetchDatasets();
      }
    } catch (error) {
      console.error('Failed to delete dataset:', error);
    }
  };

  const filteredDatasets = datasets.filter(ds =>
    ds.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <div className="relative flex-1 max-w-md">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#52525B]" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search datasets..."
              className="w-full h-10 pl-10 pr-4 bg-[#1A1A24] border border-[#2A2A3A] rounded-xl text-sm text-white placeholder:text-[#52525B] focus:outline-none focus:border-[#3B82F6]"
            />
          </div>
        </div>
        <label className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white font-medium text-sm cursor-pointer hover:opacity-90 transition-all">
          <input type="file" accept=".csv,.xlsx,.xls,.json" onChange={handleUpload} className="hidden" />
          <UploadIcon className="w-4 h-4" />
          {uploading ? 'Uploading...' : 'Upload Dataset'}
        </label>
      </div>

      {/* Datasets Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-[40vh]">
          <div className="text-[#71717A]">Loading datasets...</div>
        </div>
      ) : filteredDatasets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDatasets.map((dataset) => (
            <div
              key={dataset.id}
              className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-5 hover:border-[#3B82F6]/50 transition-all"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-2 rounded-lg bg-[#3B82F6]/10">
                  <DatasetIcon className="w-5 h-5 text-[#3B82F6]" />
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${dataset.status === 'ready' ? 'bg-[#10B981]/10 text-[#10B981]' : 'bg-[#F59E0B]/10 text-[#F59E0B]'
                  }`}>
                  {dataset.status}
                </span>
              </div>
              <h3 className="text-sm font-semibold text-white mb-1 truncate">{dataset.name}</h3>
              <p className="text-xs text-[#71717A] mb-4">{dataset.filename}</p>
              <div className="flex items-center gap-4 text-xs text-[#52525B]">
                <span>{dataset.row_count?.toLocaleString()} rows</span>
                <span>{dataset.column_count} cols</span>
                <span>{(dataset.size_bytes / 1024).toFixed(1)} KB</span>
              </div>
              <div className="flex items-center gap-2 mt-4 pt-4 border-t border-[#1E1E2A]">
                <button className="flex-1 py-2 rounded-lg bg-[#1A1A24] text-xs text-[#A1A1AA] hover:bg-[#22222E] hover:text-white transition-all">
                  Preview
                </button>
                <button
                  onClick={() => handleDelete(dataset.id)}
                  className="flex-1 py-2 rounded-lg bg-[#EF4444]/10 text-xs text-[#EF4444] hover:bg-[#EF4444]/20 transition-all"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-[40vh] text-center">
          <DatasetIcon className="w-16 h-16 mb-4 text-[#3B82F6]/50" />
          <h2 className="text-xl font-semibold text-white mb-2">No Datasets</h2>
          <p className="text-sm text-[#71717A] mb-4">Upload your first dataset to get started</p>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Analytics Page - Full implementation
// ============================================================================
function AnalyticsPage() {
  const [trends, setTrends] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [trendsRes, insightsRes] = await Promise.all([
        fetch(`${API_BASE}/analytics/trends?period=30d`),
        fetch(`${API_BASE}/analytics/insights`)
      ]);

      if (trendsRes.ok) {
        const data = await trendsRes.json();
        setTrends(data.data || []);
      }

      if (insightsRes.ok) {
        const data = await insightsRes.json();
        setInsights(data);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-[#71717A]">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      {insights && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-5">
            <p className="text-xs text-[#71717A] mb-1">Datasets Analyzed</p>
            <p className="text-2xl font-bold text-white">{insights.stats?.datasets_analyzed || 0}</p>
          </div>
          <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-5">
            <p className="text-xs text-[#71717A] mb-1">Queries Processed</p>
            <p className="text-2xl font-bold text-white">{insights.stats?.queries_processed || 0}</p>
          </div>
          <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-5">
            <p className="text-xs text-[#71717A] mb-1">Reports Generated</p>
            <p className="text-2xl font-bold text-white">{insights.stats?.reports_generated || 0}</p>
          </div>
          <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-5">
            <p className="text-xs text-[#71717A] mb-1">Success Rate</p>
            <p className="text-2xl font-bold text-[#10B981]">{insights.stats?.success_rate || 100}%</p>
          </div>
        </div>
      )}

      {/* Trends Chart */}
      <ChartContainer title="Analytics Trends" onRefresh={fetchAnalytics}>
        <div className="h-64 flex items-end justify-between gap-1 px-2">
          {trends.length > 0 ? (
            trends.map((point, i) => {
              const maxVal = Math.max(...trends.map(d => d.queries || 0));
              const height = maxVal > 0 ? ((point.queries || 0) / maxVal) * 100 : 10;
              return (
                <div
                  key={i}
                  className="flex-1 bg-gradient-to-t from-[#8B5CF6] to-[#EC4899] rounded-t-sm transition-all hover:opacity-80"
                  style={{ height: `${Math.max(height, 5)}%` }}
                  title={`${point.date}: ${point.queries}`}
                />
              );
            })
          ) : (
            <div className="w-full h-full flex items-center justify-center text-[#52525B]">
              <p className="text-sm">No trend data available</p>
            </div>
          )}
        </div>
      </ChartContainer>

      {/* Insights & Recommendations */}
      {insights && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Insights */}
          <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
            <h3 className="text-base font-semibold text-white mb-4">Key Insights</h3>
            <div className="space-y-3">
              {insights.insights?.map((insight, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[#1A1A24]">
                  <div className="w-6 h-6 rounded-full bg-[#3B82F6]/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-xs text-[#3B82F6] font-bold">{i + 1}</span>
                  </div>
                  <p className="text-sm text-[#A1A1AA]">{insight}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
            <h3 className="text-base font-semibold text-white mb-4">Recommendations</h3>
            <div className="space-y-3">
              {insights.recommendations?.map((rec, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[#1A1A24] border border-[#1E1E2A]">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${rec.priority === 'high' || rec.priority === 'critical'
                      ? 'bg-[#EF4444]/10 text-[#EF4444]'
                      : rec.priority === 'medium'
                        ? 'bg-[#F59E0B]/10 text-[#F59E0B]'
                        : 'bg-[#10B981]/10 text-[#10B981]'
                    }`}>
                    {rec.priority}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-white">{rec.title}</p>
                    <p className="text-xs text-[#71717A] mt-1">{rec.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Reports Page - Full implementation
// ============================================================================
function ReportsPage() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const res = await fetch(`${API_BASE}/reports`);
      if (res.ok) {
        const data = await res.json();
        setReports(data.reports || []);
      }
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    setGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/reports/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `Analysis Report - ${new Date().toLocaleDateString()}`,
          query: 'Analyze overall data trends and generate insights',
          report_type: 'summary'
        })
      });
      if (res.ok) {
        fetchReports();
      }
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setGenerating(false);
    }
  };

  const exportReport = async (id, format) => {
    try {
      const res = await fetch(`${API_BASE}/reports/${id}/export?format=${format}`);
      if (res.ok) {
        const data = await res.json();
        // Create download
        const content = format === 'json' ? JSON.stringify(data.content, null, 2) : data.content;
        const blob = new Blob([content], { type: data.mime_type || 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to export report:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Reports</h2>
        <button
          onClick={generateReport}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white font-medium text-sm hover:opacity-90 disabled:opacity-50 transition-all"
        >
          <PlusIcon className="w-4 h-4" />
          {generating ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      {/* Reports List */}
      {loading ? (
        <div className="flex items-center justify-center h-[40vh]">
          <div className="text-[#71717A]">Loading reports...</div>
        </div>
      ) : reports.length > 0 ? (
        <div className="space-y-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-5 hover:border-[#3B82F6]/50 transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-[#10B981]/10">
                    <DocumentIcon className="w-5 h-5 text-[#10B981]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">{report.title}</h3>
                    <p className="text-xs text-[#71717A]">
                      {new Date(report.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${report.status === 'completed' ? 'bg-[#10B981]/10 text-[#10B981]' : 'bg-[#F59E0B]/10 text-[#F59E0B]'
                  }`}>
                  {report.status}
                </span>
              </div>
              <p className="text-sm text-[#A1A1AA] mb-4 line-clamp-2">{report.summary}</p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => exportReport(report.id, 'markdown')}
                  className="px-3 py-1.5 rounded-lg bg-[#1A1A24] text-xs text-[#A1A1AA] hover:bg-[#22222E] hover:text-white transition-all"
                >
                  Export MD
                </button>
                <button
                  onClick={() => exportReport(report.id, 'html')}
                  className="px-3 py-1.5 rounded-lg bg-[#1A1A24] text-xs text-[#A1A1AA] hover:bg-[#22222E] hover:text-white transition-all"
                >
                  Export HTML
                </button>
                <button
                  onClick={() => exportReport(report.id, 'json')}
                  className="px-3 py-1.5 rounded-lg bg-[#1A1A24] text-xs text-[#A1A1AA] hover:bg-[#22222E] hover:text-white transition-all"
                >
                  Export JSON
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-[40vh] text-center">
          <DocumentIcon className="w-16 h-16 mb-4 text-[#10B981]/50" />
          <h2 className="text-xl font-semibold text-white mb-2">No Reports</h2>
          <p className="text-sm text-[#71717A] mb-4">Generate your first report to get started</p>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Settings Page - Full implementation
// ============================================================================
function SettingsPage() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/settings`);
      if (res.ok) {
        const data = await res.json();
        setSettings(data.settings);
      }
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key, value) => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [key]: value })
      });
      if (res.ok) {
        const data = await res.json();
        setSettings(data.settings);
      }
    } catch (error) {
      console.error('Failed to update settings:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="text-[#71717A]">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-lg font-semibold text-white">Settings</h2>

      {/* Appearance */}
      <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
        <h3 className="text-sm font-semibold text-white mb-4">Appearance</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">Theme</p>
              <p className="text-xs text-[#71717A]">Choose your preferred theme</p>
            </div>
            <select
              value={settings?.theme || 'dark'}
              onChange={(e) => updateSetting('theme', e.target.value)}
              className="px-3 py-2 bg-[#1A1A24] border border-[#2A2A3A] rounded-lg text-sm text-white focus:outline-none focus:border-[#3B82F6]"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="system">System</option>
            </select>
          </div>
        </div>
      </div>

      {/* Behavior */}
      <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
        <h3 className="text-sm font-semibold text-white mb-4">Behavior</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">Auto Refresh</p>
              <p className="text-xs text-[#71717A]">Automatically refresh dashboard data</p>
            </div>
            <button
              onClick={() => updateSetting('auto_refresh', !settings?.auto_refresh)}
              className={`w-12 h-6 rounded-full transition-colors ${settings?.auto_refresh ? 'bg-[#3B82F6]' : 'bg-[#2A2A3A]'
                }`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings?.auto_refresh ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">Notifications</p>
              <p className="text-xs text-[#71717A]">Enable in-app notifications</p>
            </div>
            <button
              onClick={() => updateSetting('notifications_enabled', !settings?.notifications_enabled)}
              className={`w-12 h-6 rounded-full transition-colors ${settings?.notifications_enabled ? 'bg-[#3B82F6]' : 'bg-[#2A2A3A]'
                }`}
            >
              <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${settings?.notifications_enabled ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-white">Refresh Interval</p>
              <p className="text-xs text-[#71717A]">How often to refresh data (seconds)</p>
            </div>
            <select
              value={settings?.refresh_interval || 30}
              onChange={(e) => updateSetting('refresh_interval', parseInt(e.target.value))}
              className="px-3 py-2 bg-[#1A1A24] border border-[#2A2A3A] rounded-lg text-sm text-white focus:outline-none focus:border-[#3B82F6]"
            >
              <option value={15}>15s</option>
              <option value={30}>30s</option>
              <option value={60}>60s</option>
              <option value={120}>2m</option>
            </select>
          </div>
        </div>
      </div>

      {/* API Keys */}
      <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
        <h3 className="text-sm font-semibold text-white mb-4">API Keys</h3>
        <div className="space-y-3">
          {Object.entries(settings?.api_keys || {}).map(([name, value]) => (
            <div key={name} className="flex items-center justify-between p-3 rounded-lg bg-[#1A1A24]">
              <span className="text-sm text-white">{name}</span>
              <span className="text-sm text-[#71717A] font-mono">{value}</span>
            </div>
          ))}
          {Object.keys(settings?.api_keys || {}).length === 0 && (
            <p className="text-sm text-[#71717A]">No API keys configured</p>
          )}
        </div>
      </div>

      {saving && (
        <p className="text-sm text-[#3B82F6]">Saving changes...</p>
      )}
    </div>
  );
}

// ============================================================================
// Workspace Page Component
// ============================================================================
function WorkspacePage({ onSendMessage, messages, isLoading }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) setSelectedFile(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile && !question.trim()) return;

    const qText = question.trim() || 'Analyze this dataset and summarize key insights.';

    if (selectedFile) {
      const formData = new FormData();
      const questionBlob = new Blob([qText], { type: 'text/plain' });
      const questionFile = new File([questionBlob], 'questions.txt', { type: 'text/plain' });
      formData.append('questions.txt', questionFile);
      formData.append('data.csv', selectedFile);

      onSendMessage(`Analyzing file: ${selectedFile.name}\n\nQuestion: ${qText}`, formData);
    } else {
      onSendMessage(qText);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-140px)]">
      {/* Left Panel - Input */}
      <div className="flex flex-col gap-4">
        <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
          <label className="text-xs font-semibold text-[#71717A] uppercase tracking-wider mb-3 block">
            Question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: Explain monthly revenue trends and highlight anomalies"
            className="w-full h-32 p-4 bg-[#1A1A24] border border-[#2A2A3A] rounded-xl text-sm text-white placeholder:text-[#52525B] focus:outline-none focus:border-[#3B82F6] resize-none"
          />
        </div>

        <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-6">
          <label className="text-xs font-semibold text-[#71717A] uppercase tracking-wider mb-3 block">
            Dataset
          </label>
          <div className="relative border-2 border-dashed border-[#2A2A3A] rounded-xl p-6 hover:border-[#3B82F6] transition-colors cursor-pointer text-center">
            <input
              type="file"
              accept=".csv,.xlsx,.xls,.json"
              onChange={handleFileChange}
              className="absolute inset-0 opacity-0 cursor-pointer"
            />
            <UploadIcon className="w-8 h-8 mx-auto mb-3 text-[#52525B]" />
            <p className="text-sm text-[#A1A1AA]">
              {selectedFile ? selectedFile.name : 'Drop CSV, XLSX, or JSON file here'}
            </p>
            {selectedFile && (
              <p className="text-xs text-[#71717A] mt-1">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            )}
          </div>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={!selectedFile && !question.trim()}
          className="w-full py-3 rounded-xl font-semibold bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] text-white shadow-lg shadow-blue-500/25 disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition-all"
        >
          Analyze Data
        </button>
      </div>

      {/* Right Panel - Chat */}
      <div className="h-full">
        <ChatInterface
          messages={messages}
          onSendMessage={onSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

// ============================================================================
// AI Chat Page Component
// ============================================================================
function AIChatPage({ messages, onSendMessage, isLoading }) {
  return (
    <div className="h-[calc(100vh-140px)]">
      <ChatInterface
        messages={messages}
        onSendMessage={onSendMessage}
        isLoading={isLoading}
        placeholder="Ask anything about your data..."
      />
    </div>
  );
}

// ============================================================================
// Main App Component
// ============================================================================
function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [backendHealthy, setBackendHealthy] = useState(null);

  const hasBackendUrl = useMemo(() => Boolean(BACKEND_URL), []);

  // Health check
  useEffect(() => {
    const checkHealth = async () => {
      if (!hasBackendUrl) return;
      try {
        const res = await fetch(`${API_BASE}/health`);
        setBackendHealthy(res.ok);
      } catch {
        setBackendHealthy(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [hasBackendUrl]);

  const handleSendMessage = useCallback(async (content, formData = null) => {
    setMessages(prev => [...prev, { role: 'user', content }]);
    setIsLoading(true);

    try {
      let response;

      if (formData) {
        response = await fetch(`${API_BASE}/`, {
          method: 'POST',
          body: formData,
        });
      } else {
        response = await fetch(`${API_BASE}/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: content, context: {} }),
        });
      }

      const data = await response.json();

      let replyContent = '';
      if (data.explanation) {
        replyContent = data.explanation;
      } else if (data.summary) {
        replyContent = data.summary;
      } else if (data.result) {
        replyContent = typeof data.result === 'string'
          ? data.result
          : JSON.stringify(data.result, null, 2);
      } else {
        replyContent = JSON.stringify(data, null, 2);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: replyContent,
        showActions: true
      }]);
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`
      }]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getPageTitle = () => {
    switch (activeTab) {
      case 'dashboard': return 'Dashboard';
      case 'datasets': return 'Datasets';
      case 'explorer': return 'Data Explorer';
      case 'analytics': return 'Analytics';
      case 'ai-chat': return 'AI Assistant';
      case 'reports': return 'Reports';
      case 'settings': return 'Settings';
      default: return 'Workspace';
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0A0F]">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content */}
      <main
        className={`min-h-screen transition-all duration-300 ${sidebarCollapsed ? 'ml-[72px]' : 'ml-[260px]'}`}
      >
        {/* Top Navigation */}
        <TopNav
          title={getPageTitle()}
          subtitle={backendHealthy === false ? 'Backend disconnected' : undefined}
        />

        {/* Page Content */}
        <div className="p-6">
          {activeTab === 'dashboard' && <DashboardPage />}
          {activeTab === 'explorer' && (
            <WorkspacePage
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          )}
          {activeTab === 'ai-chat' && (
            <AIChatPage
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          )}
          {activeTab === 'datasets' && <DatasetsPage />}
          {activeTab === 'analytics' && <AnalyticsPage />}
          {activeTab === 'reports' && <ReportsPage />}
          {activeTab === 'settings' && <SettingsPage />}
        </div>
      </main>
    </div>
  );
}

export default App;
