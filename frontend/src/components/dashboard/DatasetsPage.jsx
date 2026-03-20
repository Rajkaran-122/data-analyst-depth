import React, { useState, useEffect, useRef } from 'react';
import api from '../../lib/api';
import { 
  SearchIcon, UploadIcon, DatabaseIcon as DatasetIcon,
  Trash2Icon, Edit2Icon, EyeIcon, MoreHorizontalIcon,
  ArrowUpDownIcon, FileSpreadsheetIcon
} from 'lucide-react';
import DatasetPreviewModal from './DatasetPreviewModal';

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('date_desc'); // name_asc, name_desc, date_desc, size_desc
  const [isDragging, setIsDragging] = useState(false);
  
  // Upload State
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState('');
  const fileInputRef = useRef(null);

  // Modals Data
  const [previewDataset, setPreviewDataset] = useState(null);
  
  // Rename State
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');

  // Delete State
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const res = await api.get('/datasets');
      if (res.data) {
        setDatasets(res.data.datasets || []);
      }
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  // --- Upload Logic (Drag and Drop / Standard) ---
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files?.length) {
      handleUploadFile(files[0]);
    }
  };

  const handleUploadChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUploadFile(file);
    }
  };

  const handleUploadFile = async (file) => {
    // Client-side size check (50MB)
    if (file.size > 50 * 1024 * 1024) {
      setUploadError("File is too large. Maximum size is 50MB.");
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setUploadError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/datasets', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      if (res.data) {
        await fetchDatasets();
      }
    } catch (error) {
      console.error('Failed to upload dataset:', error);
      setUploadError(error.response?.data?.detail || "Upload failed.");
    } finally {
      setUploading(false);
      setUploadProgress(0);
      if (fileInputRef.current) fileInputRef.current.value = ''; // Reset input
    }
  };

  // --- Operations ---
  const handleRenameSubmit = async (datasetId) => {
    if (!editName.trim()) return setEditingId(null);
    try {
      const params = new URLSearchParams();
      params.append('name', editName.trim());
      await api.patch(`/datasets/${datasetId}`, params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      await fetchDatasets();
    } catch (error) {
      console.error("Failed to rename:", error);
      alert(error.response?.data?.detail || "Failed to rename dataset.");
    } finally {
      setEditingId(null);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deletingId) return;
    try {
      await api.delete(`/datasets/${deletingId}`);
      await fetchDatasets();
    } catch (error) {
      console.error('Failed to delete dataset:', error);
    } finally {
      setDeletingId(null);
    }
  };

  // --- Sorting & Filtering ---
  let processedDatasets = datasets.filter(ds =>
    ds.name.toLowerCase().includes(search.toLowerCase())
  );

  processedDatasets.sort((a, b) => {
    if (sortBy === 'name_asc') return a.name.localeCompare(b.name);
    if (sortBy === 'name_desc') return b.name.localeCompare(a.name);
    if (sortBy === 'date_desc') return new Date(b.uploaded_at) - new Date(a.uploaded_at);
    if (sortBy === 'size_desc') return b.size_bytes - a.size_bytes;
    return 0;
  });

  return (
    <div className="space-y-6">
      {/* Search & Header Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4 w-full sm:w-auto flex-1">
          <div className="relative flex-1 max-w-md">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#52525B]" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search datasets..."
              className="w-full h-10 pl-10 pr-4 bg-[#12121A] border border-[#2A2A3A] rounded-xl text-sm text-white placeholder:text-[#52525B] focus:outline-none focus:border-[#3B82F6] transition-all"
            />
          </div>
          
          <div className="relative">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="appearance-none h-10 pl-10 pr-8 bg-[#12121A] border border-[#2A2A3A] rounded-xl text-sm text-[#A1A1AA] hover:text-white cursor-pointer focus:outline-none focus:border-[#3B82F6] transition-all"
            >
              <option value="date_desc">Newest First</option>
              <option value="name_asc">Name (A-Z)</option>
              <option value="name_desc">Name (Z-A)</option>
              <option value="size_desc">Largest First</option>
            </select>
            <ArrowUpDownIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#52525B]" />
          </div>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div 
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative w-full border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center transition-all ${
          isDragging ? 'border-[#3B82F6] bg-[#3B82F6]/5' : 'border-[#2A2A3A] bg-[#12121A]/50 hover:bg-[#12121A]'
        }`}
      >
        <div className="w-16 h-16 mb-4 rounded-full bg-[#3B82F6]/10 flex items-center justify-center">
          <UploadIcon className={`w-8 h-8 ${isDragging ? 'text-[#3B82F6] animate-bounce' : 'text-[#3B82F6]/70'}`} />
        </div>
        
        {uploading ? (
          <div className="w-full max-w-xs text-center">
            <div className="flex justify-between text-xs text-[#A1A1AA] mb-2">
              <span>Uploading Dataset...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full h-2 bg-[#1A1A24] rounded-full overflow-hidden">
              <div 
                className="h-full bg-[#3B82F6] transition-all duration-300 ease-out" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="text-center">
            <h3 className="text-base font-semibold text-white mb-2">Drag & Drop your dataset here</h3>
            <p className="text-sm text-[#71717A] mb-4">Support for .csv, .json, and .xlsx (Max 50MB)</p>
            <label className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#3B82F6] hover:bg-[#2563EB] text-white font-medium text-sm cursor-pointer transition-colors shadow-lg shadow-[#3B82F6]/20">
              <input 
                type="file" 
                accept=".csv,.xlsx,.xls,.json" 
                onChange={handleUploadChange} 
                className="hidden" 
                ref={fileInputRef}
              />
              Select File
            </label>
            {uploadError && <p className="mt-4 text-sm text-[#EF4444] font-medium">{uploadError}</p>}
          </div>
        )}
      </div>

      {/* Datasets Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="text-[#71717A] animate-pulse">Loading datasets...</div>
        </div>
      ) : processedDatasets.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {processedDatasets.map((dataset) => (
            <div
              key={dataset.id}
              className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl p-5 hover:border-[#3B82F6]/40 transition-all flex flex-col group relative overflow-hidden"
            >
              {/* Highlight bar at top */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#3B82F6] to-[#8B5CF6] opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="flex items-start justify-between mb-4">
                <div className="p-2.5 rounded-xl bg-[#1A1A24] text-[#A1A1AA] group-hover:bg-[#3B82F6]/10 group-hover:text-[#3B82F6] transition-colors">
                  <FileSpreadsheetIcon className="w-6 h-6" />
                </div>
                
                {/* Actions Menu Trigger (Hover) */}
                <div className="flex opacity-0 group-hover:opacity-100 transition-opacity space-x-1">
                  <button 
                    onClick={() => {
                      setEditingId(dataset.id);
                      setEditName(dataset.name);
                    }}
                    className="p-1.5 rounded-lg text-[#71717A] hover:text-white hover:bg-[#1A1A24]"
                    title="Rename"
                  >
                    <Edit2Icon className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => setDeletingId(dataset.id)}
                    className="p-1.5 rounded-lg text-[#EF4444]/70 hover:text-[#EF4444] hover:bg-[#EF4444]/10"
                    title="Delete"
                  >
                    <Trash2Icon className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Title Section (with inline edit) */}
              {editingId === dataset.id ? (
                <div className="mb-2">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleRenameSubmit(dataset.id);
                      if (e.key === 'Escape') setEditingId(null);
                    }}
                    autoFocus
                    onBlur={() => handleRenameSubmit(dataset.id)}
                    className="w-full bg-[#1A1A24] border border-[#3B82F6] rounded px-2 py-1 text-sm text-white focus:outline-none"
                  />
                </div>
              ) : (
                <div className="mb-2">
                  <h3 className="text-base font-semibold text-white truncate pr-2 group-hover:text-[#3B82F6] transition-colors" title={dataset.name}>
                    {dataset.name}
                  </h3>
                  <p className="text-xs text-[#52525B] truncate mt-0.5" title={dataset.filename}>
                    {dataset.filename}
                  </p>
                </div>
              )}

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mt-2 mb-4">
                <span className="px-2 py-1 rounded bg-[#1A1A24] text-[10px] font-medium text-[#A1A1AA]">
                  {(dataset.size_bytes / 1024 / 1024).toFixed(2)} MB
                </span>
                <span className="px-2 py-1 rounded bg-[#1A1A24] text-[10px] font-medium text-[#A1A1AA]">
                  {dataset.row_count?.toLocaleString()} Rows
                </span>
                <span className="px-2 py-1 rounded bg-[#1A1A24] text-[10px] font-medium text-[#A1A1AA]">
                  {dataset.column_count} Cols
                </span>
              </div>

              <div className="mt-auto pt-4 flex items-center justify-between border-t border-[#1E1E2A]">
                <p className="text-xs text-[#52525B]">
                  {new Date(dataset.uploaded_at).toLocaleDateString()}
                </p>
                <button 
                  onClick={() => setPreviewDataset(dataset)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#3B82F6]/10 text-[#3B82F6] text-xs font-medium hover:bg-[#3B82F6] hover:text-white transition-all"
                >
                  <EyeIcon className="w-3.5 h-3.5" />
                  Preview & Schema
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-64 border border-dashed border-[#2A2A3A] rounded-2xl bg-[#0A0A0F]/50">
          <DatasetIcon className="w-12 h-12 mb-4 text-[#52525B]" />
          <h2 className="text-lg font-semibold text-white mb-2">No Datasets Found</h2>
          <p className="text-sm text-[#71717A]">Upload a dataset above to get started.</p>
        </div>
      )}

      {/* Preview Modal */}
      <DatasetPreviewModal 
        isOpen={!!previewDataset} 
        onClose={() => setPreviewDataset(null)} 
        dataset={previewDataset} 
      />

      {/* Delete Confirmation Modal */}
      {deletingId && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#12121A] border border-[#1E1E2A] rounded-2xl w-full max-w-sm p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
            <h3 className="text-lg font-semibold text-white mb-2">Delete Dataset?</h3>
            <p className="text-sm text-[#A1A1AA] mb-6">
              This action cannot be undone. This dataset and any associated insights will be permanently removed.
            </p>
            <div className="flex items-center justify-end gap-3">
              <button 
                onClick={() => setDeletingId(null)}
                className="px-4 py-2 rounded-xl text-sm font-medium text-[#A1A1AA] hover:text-white hover:bg-[#1A1A24] transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={handleDeleteConfirm}
                className="px-4 py-2 rounded-xl text-sm font-medium bg-[#EF4444] text-white hover:bg-[#DC2626] transition-colors shadow-lg shadow-[#EF4444]/20"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
