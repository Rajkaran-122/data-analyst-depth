import React, { useState, useEffect, useCallback } from 'react';
import api from '../../lib/api';
import {
  DownloadIcon,
  Loader2Icon,
  CheckCircle2Icon,
  AlertCircleIcon,
  FilterIcon,
  XIcon,
  PlusIcon,
  SparklesIcon,
  BrainCircuitIcon,
  FileSpreadsheetIcon,
  FileJsonIcon,
  FileTextIcon,
  Trash2Icon,
  ShieldCheckIcon,
  ColumnsIcon,
  CheckIcon,
  BarChart3Icon,
  TrendingUpIcon,
  ZapIcon,
  HardDriveIcon,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Toast Notification
// ---------------------------------------------------------------------------
function Toast({ show, type, message, onClose }) {
  if (!show) return null;
  const styles = {
    success: 'bg-[#10B981]/10 border-[#10B981]/30 text-[#10B981]',
    error: 'bg-[#EF4444]/10 border-[#EF4444]/30 text-[#EF4444]',
    info: 'bg-[#3B82F6]/10 border-[#3B82F6]/30 text-[#3B82F6]',
    warning: 'bg-[#F59E0B]/10 border-[#F59E0B]/30 text-[#F59E0B]',
  };
  const icons = {
    success: <CheckCircle2Icon className="w-4 h-4 flex-shrink-0" />,
    error: <AlertCircleIcon className="w-4 h-4 flex-shrink-0" />,
    info: <DownloadIcon className="w-4 h-4 flex-shrink-0" />,
    warning: <AlertCircleIcon className="w-4 h-4 flex-shrink-0" />,
  };
  return (
    <div className={`fixed bottom-6 right-6 z-[100] flex items-center gap-3 px-4 py-3 rounded-xl border shadow-2xl backdrop-blur-md animate-in slide-in-from-bottom-5 duration-300 ${styles[type] || styles.info}`}>
      {icons[type]}
      <span className="text-sm font-medium max-w-xs">{message}</span>
      <button onClick={onClose} className="ml-2 opacity-60 hover:opacity-100"><XIcon className="w-3.5 h-3.5" /></button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Quality Score Ring
// ---------------------------------------------------------------------------
function QualityRing({ score, grade, size = 80 }) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 90 ? '#10B981' : score >= 75 ? '#3B82F6' : score >= 60 ? '#F59E0B' : '#EF4444';

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#1E1E2A" strokeWidth="6" />
          <circle
            cx={size/2} cy={size/2} r={radius} fill="none"
            stroke={color} strokeWidth="6" strokeLinecap="round"
            strokeDasharray={circumference} strokeDashoffset={offset}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold text-white">{score}</span>
        </div>
      </div>
      <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color }}>{grade}</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Quality Dimension Bar
// ---------------------------------------------------------------------------
function QualityBar({ label, value, icon: Icon }) {
  const color = value >= 90 ? '#10B981' : value >= 75 ? '#3B82F6' : value >= 60 ? '#F59E0B' : '#EF4444';
  return (
    <div className="flex items-center gap-3">
      <Icon className="w-3.5 h-3.5 text-[#71717A] flex-shrink-0" />
      <span className="text-xs text-[#A1A1AA] w-24 flex-shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-[#1E1E2A] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${value}%`, backgroundColor: color }} />
      </div>
      <span className="text-xs font-medium text-white w-12 text-right">{value}%</span>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Format Selector
// ---------------------------------------------------------------------------
function FormatSelector({ value, onChange, estimates }) {
  const fmtSize = (bytes) => {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };
  const formats = [
    { id: 'csv', label: 'CSV', icon: FileTextIcon, desc: 'Universal' },
    { id: 'json', label: 'JSON', icon: FileJsonIcon, desc: 'Structured' },
    { id: 'xlsx', label: 'Excel', icon: FileSpreadsheetIcon, desc: 'Workbook' },
  ];
  return (
    <div className="flex gap-2">
      {formats.map((f) => {
        const Icon = f.icon;
        const active = value === f.id;
        const est = estimates?.[f.id];
        return (
          <button
            key={f.id}
            onClick={() => onChange(f.id)}
            className={`flex flex-col items-center gap-1 px-4 py-2.5 rounded-xl text-xs font-medium border transition-all ${
              active
                ? 'border-[#3B82F6] bg-[#3B82F6]/10 text-[#3B82F6] shadow-lg shadow-[#3B82F6]/10'
                : 'border-[#2A2A3A] bg-[#1A1A24] text-[#71717A] hover:text-white hover:border-[#3B82F6]/40'
            }`}
          >
            <div className="flex items-center gap-1.5">
              <Icon className="w-3.5 h-3.5" />
              {f.label}
            </div>
            {est ? <span className="text-[10px] opacity-70">~{fmtSize(est)}</span> : null}
          </button>
        );
      })}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Column Selector
// ---------------------------------------------------------------------------
function ColumnSelector({ columns, selected, onChange }) {
  const allSelected = selected.length === 0 || selected.length === columns.length;

  const toggleAll = () => {
    onChange(allSelected ? [] : columns.map(c => c.name));
  };

  const toggle = (name) => {
    if (allSelected) {
      // First click after "all" — deselect this one
      onChange(columns.map(c => c.name).filter(n => n !== name));
    } else if (selected.includes(name)) {
      const next = selected.filter(n => n !== name);
      onChange(next.length === 0 ? [] : next); // empty = all
    } else {
      const next = [...selected, name];
      onChange(next.length === columns.length ? [] : next);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] text-[#52525B]">
          {allSelected ? `All ${columns.length} columns` : `${selected.length} of ${columns.length} columns`}
        </span>
        <button onClick={toggleAll} className="text-[10px] text-[#3B82F6] hover:underline">
          {allSelected ? 'Deselect All' : 'Select All'}
        </button>
      </div>
      <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto pr-1">
        {columns.map((col) => {
          const isActive = allSelected || selected.includes(col.name);
          return (
            <button
              key={col.name}
              onClick={() => toggle(col.name)}
              className={`flex items-center gap-1 px-2 py-1 rounded-md text-[11px] font-medium border transition-all ${
                isActive
                  ? 'border-[#3B82F6]/40 bg-[#3B82F6]/10 text-[#3B82F6]'
                  : 'border-[#2A2A3A] bg-[#1A1A24] text-[#52525B] hover:text-[#A1A1AA]'
              }`}
              title={`${col.name} (${col.dtype})`}
            >
              {isActive && <CheckIcon className="w-2.5 h-2.5" />}
              <span className="truncate max-w-[100px]">{col.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Filter Builder
// ---------------------------------------------------------------------------
function FilterBar({ columns, filters, onFiltersChange }) {
  const operators = [
    { id: 'eq', label: '=' }, { id: 'neq', label: '≠' },
    { id: 'contains', label: 'contains' },
    { id: 'gt', label: '>' }, { id: 'gte', label: '≥' },
    { id: 'lt', label: '<' }, { id: 'lte', label: '≤' },
    { id: 'isnull', label: 'is null' }, { id: 'notnull', label: 'not null' },
  ];

  const addFilter = () => {
    onFiltersChange([...filters, { column: columns[0]?.name || '', operator: 'eq', value: '' }]);
  };
  const removeFilter = (idx) => onFiltersChange(filters.filter((_, i) => i !== idx));
  const updateFilter = (idx, key, val) => {
    onFiltersChange(filters.map((f, i) => (i === idx ? { ...f, [key]: val } : f)));
  };

  return (
    <div className="space-y-2">
      {filters.map((filter, idx) => (
        <div key={idx} className="flex items-center gap-2 animate-in fade-in slide-in-from-top-1 duration-200">
          <select value={filter.column} onChange={(e) => updateFilter(idx, 'column', e.target.value)}
            className="h-9 px-3 bg-[#1A1A24] border border-[#2A2A3A] rounded-lg text-xs text-white focus:outline-none focus:border-[#3B82F6] min-w-[130px]">
            {columns.map((c) => <option key={c.name} value={c.name}>{c.name}</option>)}
          </select>
          <select value={filter.operator} onChange={(e) => updateFilter(idx, 'operator', e.target.value)}
            className="h-9 px-2 bg-[#1A1A24] border border-[#2A2A3A] rounded-lg text-xs text-white focus:outline-none focus:border-[#3B82F6]">
            {operators.map((op) => <option key={op.id} value={op.id}>{op.label}</option>)}
          </select>
          {!['isnull', 'notnull'].includes(filter.operator) && (
            <input type="text" value={filter.value} onChange={(e) => updateFilter(idx, 'value', e.target.value)}
              placeholder="Value..." className="h-9 px-3 bg-[#1A1A24] border border-[#2A2A3A] rounded-lg text-xs text-white placeholder:text-[#52525B] focus:outline-none focus:border-[#3B82F6] flex-1 min-w-[100px]" />
          )}
          <button onClick={() => removeFilter(idx)} className="p-2 rounded-lg text-[#EF4444]/60 hover:text-[#EF4444] hover:bg-[#EF4444]/10 transition-colors">
            <Trash2Icon className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}
      <button onClick={addFilter} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-[#3B82F6] hover:bg-[#3B82F6]/10 transition-colors">
        <PlusIcon className="w-3.5 h-3.5" /> Add Filter
      </button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Download Panel
// ---------------------------------------------------------------------------
export default function DownloadPanel({ isOpen, onClose, dataset }) {
  const [format, setFormat] = useState('csv');
  const [filters, setFilters] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [downloading, setDownloading] = useState(null);
  const [toast, setToast] = useState({ show: false, type: 'info', message: '' });
  const [cleanedPreview, setCleanedPreview] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [activeSection, setActiveSection] = useState('options'); // 'options' | 'filters' | 'columns'

  useEffect(() => {
    if (isOpen && dataset) {
      fetchCleanedPreview();
    }
    return () => {
      setCleanedPreview(null);
      setFilters([]);
      setSelectedColumns([]);
      setActiveSection('options');
    };
  }, [isOpen, dataset]);

  const fetchCleanedPreview = async () => {
    setPreviewLoading(true);
    try {
      const res = await api.get(`/datasets/${dataset.id}/preview/cleaned?rows=20`);
      setCleanedPreview(res.data);
    } catch (err) {
      console.error('Failed to fetch cleaned preview:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const showToast = (type, message) => {
    setToast({ show: true, type, message });
    setTimeout(() => setToast({ show: false, type: 'info', message: '' }), 4500);
  };

  const triggerDownload = useCallback(async (variant) => {
    setDownloading(variant);
    try {
      let response;
      const config = { responseType: 'blob' };

      if (variant === 'filtered') {
        response = await api.post(
          `/datasets/${dataset.id}/download/filtered`,
          { filters, columns: selectedColumns.length > 0 ? selectedColumns : null, format },
          config
        );
      } else {
        response = await api.get(
          `/datasets/${dataset.id}/download/${variant}?format=${format}`,
          config
        );
      }

      const disposition = response.headers['content-disposition'] || '';
      const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch ? filenameMatch[1] : `${dataset.name}_${variant}.${format}`;

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      const sizeMB = (response.data.size / 1024 / 1024).toFixed(2);
      showToast('success', `✅ ${filename} downloaded (${sizeMB} MB)`);
    } catch (err) {
      console.error('Download failed:', err);
      showToast('error', `Download failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setDownloading(null);
    }
  }, [dataset, format, filters, selectedColumns]);

  if (!isOpen || !dataset) return null;

  const columns = cleanedPreview?.columns || dataset.columns || [];
  const quality = cleanedPreview?.quality_score || null;
  const estimates = cleanedPreview?.estimated_sizes || null;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
        <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl w-full max-w-4xl max-h-[88vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
          
          {/* Header */}
          <div className="flex items-center justify-between p-5 border-b border-[#1E1E2A]">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-[#3B82F6]/20 to-[#8B5CF6]/20">
                <DownloadIcon className="w-5 h-5 text-[#3B82F6]" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Download Data</h2>
                <p className="text-xs text-[#71717A] mt-0.5">
                  {dataset.name} • {dataset.row_count?.toLocaleString()} rows • {dataset.column_count} cols
                </p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24] transition-colors">
              <XIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-5 space-y-5">

            {/* Quality Score + Cleaning Summary */}
            {previewLoading ? (
              <div className="flex items-center justify-center py-10">
                <Loader2Icon className="w-6 h-6 animate-spin text-[#3B82F6]" />
                <span className="ml-3 text-sm text-[#71717A]">Analysing dataset quality…</span>
              </div>
            ) : cleanedPreview && (
              <div className="bg-[#0A0A0F] border border-[#1E1E2A] rounded-xl p-5">
                <div className="flex flex-col sm:flex-row gap-6">
                  {/* Left: Quality Ring */}
                  {quality && (
                    <div className="flex flex-col items-center gap-3 sm:border-r sm:border-[#1E1E2A] sm:pr-6">
                      <h3 className="text-[10px] font-semibold text-[#71717A] uppercase tracking-wider">Data Quality</h3>
                      <QualityRing score={quality.overall} grade={quality.grade} />
                    </div>
                  )}
                  {/* Right: Stats + Dimensions */}
                  <div className="flex-1 space-y-4">
                    {/* Row Stats */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="bg-[#12121A] rounded-lg p-3 text-center">
                        <div className="text-base font-bold text-white">{cleanedPreview.original_rows?.toLocaleString()}</div>
                        <div className="text-[10px] text-[#71717A] mt-0.5">Original</div>
                      </div>
                      <div className="bg-[#12121A] rounded-lg p-3 text-center">
                        <div className="text-base font-bold text-[#10B981]">{cleanedPreview.cleaned_rows?.toLocaleString()}</div>
                        <div className="text-[10px] text-[#71717A] mt-0.5">After Clean</div>
                      </div>
                      <div className="bg-[#12121A] rounded-lg p-3 text-center">
                        <div className="text-base font-bold text-[#F59E0B]">{cleanedPreview.rows_removed?.toLocaleString()}</div>
                        <div className="text-[10px] text-[#71717A] mt-0.5">Removed</div>
                      </div>
                      <div className="bg-[#12121A] rounded-lg p-3 text-center">
                        <div className="text-base font-bold text-[#8B5CF6]">{cleanedPreview.column_count}</div>
                        <div className="text-[10px] text-[#71717A] mt-0.5">Columns</div>
                      </div>
                    </div>
                    {/* Quality Dimensions */}
                    {quality && (
                      <div className="space-y-2">
                        <QualityBar label="Completeness" value={quality.completeness} icon={CheckCircle2Icon} />
                        <QualityBar label="Uniqueness" value={quality.uniqueness} icon={ZapIcon} />
                        <QualityBar label="Consistency" value={quality.consistency} icon={BarChart3Icon} />
                        <QualityBar label="Validity" value={quality.validity} icon={ShieldCheckIcon} />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Section Tabs */}
            <div className="flex gap-1 bg-[#0A0A0F] p-1 rounded-xl border border-[#1E1E2A]">
              {[
                { id: 'options', label: 'Download Options', icon: DownloadIcon },
                { id: 'filters', label: `Filters${filters.length ? ` (${filters.length})` : ''}`, icon: FilterIcon },
                { id: 'columns', label: `Columns${selectedColumns.length ? ` (${selectedColumns.length})` : ''}`, icon: ColumnsIcon },
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveSection(tab.id)}
                    className={`flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      activeSection === tab.id
                        ? 'bg-[#1A1A24] text-white shadow-sm'
                        : 'text-[#71717A] hover:text-white'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            {/* Filters Section */}
            {activeSection === 'filters' && (
              <div className="bg-[#0A0A0F] border border-[#1E1E2A] rounded-xl p-4 animate-in fade-in duration-200">
                <FilterBar columns={columns} filters={filters} onFiltersChange={setFilters} />
                {filters.length > 0 && (
                  <p className="text-xs text-[#52525B] mt-2 italic">Filters apply to "Download Filtered Data".</p>
                )}
              </div>
            )}

            {/* Column Selector Section */}
            {activeSection === 'columns' && (
              <div className="bg-[#0A0A0F] border border-[#1E1E2A] rounded-xl p-4 animate-in fade-in duration-200">
                <ColumnSelector columns={columns} selected={selectedColumns} onChange={setSelectedColumns} />
                {selectedColumns.length > 0 && (
                  <p className="text-xs text-[#52525B] mt-2 italic">Column selection applies to "Download Filtered Data".</p>
                )}
              </div>
            )}

            {/* Format Selection */}
            {activeSection === 'options' && (
              <>
                <div>
                  <h3 className="text-xs font-semibold text-[#71717A] uppercase tracking-wider mb-3 flex items-center gap-2">
                    <HardDriveIcon className="w-3.5 h-3.5" /> Export Format
                  </h3>
                  <FormatSelector value={format} onChange={setFormat} estimates={estimates} />
                </div>

                {/* Download Buttons */}
                <div className="space-y-3">
                  <h3 className="text-xs font-semibold text-[#71717A] uppercase tracking-wider">Choose Export Type</h3>

                  {/* Raw */}
                  <button onClick={() => triggerDownload('raw')} disabled={!!downloading}
                    className="w-full flex items-center gap-4 p-4 rounded-xl border border-[#2A2A3A] bg-[#1A1A24] hover:bg-[#22222E] hover:border-[#3B82F6]/40 transition-all disabled:opacity-50 group">
                    <div className="p-2 rounded-lg bg-[#52525B]/10 group-hover:bg-[#3B82F6]/10 transition-colors">
                      <FileSpreadsheetIcon className="w-5 h-5 text-[#A1A1AA] group-hover:text-[#3B82F6] transition-colors" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="text-sm font-medium text-white">Download Raw Data</div>
                      <div className="text-xs text-[#71717A] mt-0.5">Original uploaded file, no modifications</div>
                    </div>
                    {downloading === 'raw'
                      ? <Loader2Icon className="w-5 h-5 animate-spin text-[#3B82F6]" />
                      : <DownloadIcon className="w-5 h-5 text-[#52525B] group-hover:text-[#3B82F6] transition-colors" />}
                  </button>

                  {/* Cleaned */}
                  <button onClick={() => triggerDownload('cleaned')} disabled={!!downloading}
                    className="w-full flex items-center gap-4 p-4 rounded-xl border border-[#3B82F6]/30 bg-gradient-to-r from-[#3B82F6]/5 to-transparent hover:from-[#3B82F6]/10 transition-all disabled:opacity-50 group">
                    <div className="p-2 rounded-lg bg-[#3B82F6]/10">
                      <SparklesIcon className="w-5 h-5 text-[#3B82F6]" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="text-sm font-medium text-white flex items-center gap-2">
                        Download Cleaned Data
                        {quality && <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#3B82F6]/10 text-[#3B82F6]">{quality.grade}</span>}
                      </div>
                      <div className="text-xs text-[#71717A] mt-0.5">Deduplicated, type-coerced, nulls handled, names standardised</div>
                    </div>
                    {downloading === 'cleaned'
                      ? <Loader2Icon className="w-5 h-5 animate-spin text-[#3B82F6]" />
                      : <DownloadIcon className="w-5 h-5 text-[#3B82F6]" />}
                  </button>

                  {/* Filtered */}
                  <button onClick={() => triggerDownload('filtered')} disabled={!!downloading || (filters.length === 0 && selectedColumns.length === 0)}
                    className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all disabled:opacity-40 group ${
                      (filters.length > 0 || selectedColumns.length > 0)
                        ? 'border-[#8B5CF6]/30 bg-gradient-to-r from-[#8B5CF6]/5 to-transparent hover:from-[#8B5CF6]/10'
                        : 'border-[#2A2A3A] bg-[#1A1A24]'
                    }`}>
                    <div className={`p-2 rounded-lg ${(filters.length > 0 || selectedColumns.length > 0) ? 'bg-[#8B5CF6]/10' : 'bg-[#52525B]/10'}`}>
                      <FilterIcon className={`w-5 h-5 ${(filters.length > 0 || selectedColumns.length > 0) ? 'text-[#8B5CF6]' : 'text-[#52525B]'}`} />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="text-sm font-medium text-white">Download Filtered Data</div>
                      <div className="text-xs text-[#71717A] mt-0.5">
                        {filters.length > 0 || selectedColumns.length > 0
                          ? `Cleaned + ${filters.length} filter${filters.length !== 1 ? 's' : ''}${selectedColumns.length > 0 ? ` + ${selectedColumns.length} cols` : ''}`
                          : 'Use the Filters / Columns tabs to configure'}
                      </div>
                    </div>
                    {downloading === 'filtered'
                      ? <Loader2Icon className="w-5 h-5 animate-spin text-[#8B5CF6]" />
                      : <DownloadIcon className={`w-5 h-5 ${(filters.length > 0 || selectedColumns.length > 0) ? 'text-[#8B5CF6]' : 'text-[#52525B]'}`} />}
                  </button>

                  {/* Model-Ready */}
                  <button onClick={() => triggerDownload('model-ready')} disabled={!!downloading}
                    className="w-full flex items-center gap-4 p-4 rounded-xl border border-[#10B981]/30 bg-gradient-to-r from-[#10B981]/5 to-transparent hover:from-[#10B981]/10 transition-all disabled:opacity-50 group">
                    <div className="p-2 rounded-lg bg-[#10B981]/10">
                      <BrainCircuitIcon className="w-5 h-5 text-[#10B981]" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-white">Download Model-Ready Data</span>
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#10B981]/10 text-[#10B981] uppercase">ML</span>
                      </div>
                      <div className="text-xs text-[#71717A] mt-0.5">Cleaned + imputed + encoded + normalised [0,1]</div>
                    </div>
                    {downloading === 'model-ready'
                      ? <Loader2Icon className="w-5 h-5 animate-spin text-[#10B981]" />
                      : <DownloadIcon className="w-5 h-5 text-[#10B981]" />}
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Footer */}
          <div className="px-5 py-3 border-t border-[#1E1E2A] bg-[#0A0A0F] flex items-center justify-between">
            <p className="text-xs text-[#52525B]">UTF-8 BOM for Excel • Streaming export</p>
            <button onClick={onClose} className="px-4 py-2 rounded-xl text-sm font-medium text-[#A1A1AA] hover:text-white hover:bg-[#1A1A24] transition-colors">
              Close
            </button>
          </div>
        </div>
      </div>
      <Toast {...toast} onClose={() => setToast({ show: false, type: 'info', message: '' })} />
    </>
  );
}
