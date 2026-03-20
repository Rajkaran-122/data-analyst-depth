import React, { useState, useEffect } from 'react';
import api from '../../lib/api';
import { XIcon, TableIcon, CodeIcon, Loader2Icon } from 'lucide-react';

export default function DatasetPreviewModal({ isOpen, onClose, dataset }) {
  const [activeTab, setActiveTab] = useState('data'); // 'data' | 'schema'
  const [previewData, setPreviewData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && dataset) {
      fetchPreview();
      setActiveTab('data');
    }
  }, [isOpen, dataset]);

  const fetchPreview = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`/datasets/${dataset.id}/preview?rows=100`);
      setPreviewData(res.data.preview || []);
      setColumns(res.data.columns || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load preview');
      setPreviewData([]);
      setColumns([]);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl w-full max-w-5xl h-[80vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#1E1E2A]">
          <div>
            <h2 className="text-lg font-semibold text-white">{dataset?.name}</h2>
            <p className="text-sm text-[#71717A] mt-0.5">
              {dataset?.filename} • {(dataset?.size_bytes / 1024 / 1024).toFixed(2)} MB • {dataset?.row_count?.toLocaleString()} rows
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24] transition-colors"
          >
            <XIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-6 px-4 py-2 border-b border-[#1E1E2A] bg-[#0A0A0F]">
          <button
            onClick={() => setActiveTab('data')}
            className={`flex items-center gap-2 px-1 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'data'
                ? 'border-[#3B82F6] text-[#3B82F6]'
                : 'border-transparent text-[#71717A] hover:text-white'
            }`}
          >
            <TableIcon className="w-4 h-4" />
            Data Preview
          </button>
          <button
            onClick={() => setActiveTab('schema')}
            className={`flex items-center gap-2 px-1 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === 'schema'
                ? 'border-[#8B5CF6] text-[#8B5CF6]'
                : 'border-transparent text-[#71717A] hover:text-white'
            }`}
          >
            <CodeIcon className="w-4 h-4" />
            Schema Details
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-auto bg-[#0A0A0F] relative">
          {loading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-[#71717A]">
              <Loader2Icon className="w-8 h-8 animate-spin mb-4 text-[#3B82F6]" />
              <p>Loading preview data...</p>
            </div>
          ) : error ? (
            <div className="absolute inset-0 flex items-center justify-center text-[#EF4444] px-4 text-center">
              <p>{error}</p>
            </div>
          ) : activeTab === 'data' ? (
            <div className="h-full overflow-auto">
              {previewData.length > 0 ? (
                <table className="w-full text-left text-sm text-[#A1A1AA] whitespace-nowrap">
                  <thead className="text-xs text-[#71717A] bg-[#12121A] sticky top-0 z-10 shadow-md">
                    <tr>
                      <th className="px-4 py-3 font-medium border-b border-[#1E1E2A] border-r border-[#1E1E2A] w-16 bg-[#12121A]">#</th>
                      {columns.map((col, idx) => (
                        <th key={idx} className="px-4 py-3 font-medium border-b border-[#1E1E2A] bg-[#12121A]">
                          {col.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.map((row, rowIndex) => (
                      <tr key={rowIndex} className="border-b border-[#1E1E2A] hover:bg-[#1A1A24] transition-colors">
                        <td className="px-4 py-2 border-r border-[#1E1E2A] text-[#71717A] text-xs">
                          {rowIndex + 1}
                        </td>
                        {columns.map((col, colIndex) => (
                          <td key={colIndex} className="px-4 py-2">
                            {row[col.name] !== null && row[col.name] !== undefined ? String(row[col.name]) : <span className="text-[#EF4444]/50 italic">null</span>}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="h-full flex items-center justify-center text-[#71717A]">
                  No data available for preview.
                </div>
              )}
            </div>
          ) : (
            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {columns.map((col, idx) => (
                  <div key={idx} className="bg-[#12121A] border border-[#1E1E2A] rounded-xl p-4 flex flex-col">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold text-white truncate pr-2" title={col.name}>
                        {col.name}
                      </h3>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#3B82F6]/10 text-[#3B82F6] flex-shrink-0">
                        {col.dtype}
                      </span>
                    </div>
                    
                    <div className={`mt-2 mb-3 px-2 py-1.5 rounded text-xs flex items-center justify-between ${
                      col.null_percentage > 50 ? 'bg-[#EF4444]/10 text-[#EF4444]' :
                      col.null_percentage > 0 ? 'bg-[#F59E0B]/10 text-[#F59E0B]' :
                      'bg-[#10B981]/10 text-[#10B981]'
                    }`}>
                      <span>Missing Values</span>
                      <span className="font-semibold">{col.null_percentage}%</span>
                    </div>

                    <div className="mt-auto">
                      <p className="text-xs text-[#71717A] mb-1.5">Sample Values:</p>
                      <div className="flex flex-wrap gap-1.5">
                        {col.sample_values?.length > 0 ? (
                          col.sample_values.map((val, vIdx) => (
                            <span key={vIdx} className="px-1.5 py-0.5 rounded bg-[#1A1A24] border border-[#2A2A3A] text-xs text-[#A1A1AA] truncate max-w-[120px]" title={String(val)}>
                              {String(val)}
                            </span>
                          ))
                        ) : (
                          <span className="text-xs text-[#52525B] italic">No samples</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="px-4 py-3 border-t border-[#1E1E2A] bg-[#12121A] text-xs text-[#71717A] flex justify-between items-center">
          <span>Displaying up to 100 preview rows.</span>
          <span>{columns.length} Total Columns</span>
        </div>

      </div>
    </div>
  );
}
