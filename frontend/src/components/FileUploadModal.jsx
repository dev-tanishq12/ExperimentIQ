// frontend/src/components/FileUploadModal.jsx
import React, { useState } from 'react';
import { X, UploadCloud, FileSpreadsheet, Settings } from 'lucide-react';

export default function FileUploadModal({ isOpen, onClose, onUpload, loading }) {
  if (!isOpen) return null;

  const [file, setFile] = useState(null);
  const [groupCol, setGroupCol] = useState('experiment_group');
  const [userCol, setUserCol] = useState('user_id');
  const [convCol, setConvCol] = useState('conversion');
  const [alpha, setAlpha] = useState(0.05);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);
    formData.append('group_column', groupCol);
    formData.append('user_column', userCol);
    formData.append('conversion_col', convCol);
    formData.append('alpha', alpha);

    onUpload(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="glass-card max-w-lg w-full p-6 sm:p-8 bg-gray-900 border border-white/20 relative shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white p-1 rounded-lg hover:bg-white/10"
        >
          <X size={20} />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <UploadCloud size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Upload Experiment Dataset</h2>
            <p className="text-xs text-gray-400">Supported formats: CSV, XLSX, XLS</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* File input dropzone */}
          <div className="border-2 border-dashed border-white/15 hover:border-indigo-500/50 rounded-xl p-6 text-center cursor-pointer transition-colors bg-white/[0.02]">
            <input
              type="file"
              accept=".csv, .xlsx, .xls"
              onChange={(e) => setFile(e.target.files[0])}
              className="hidden"
              id="file-upload"
              required
            />
            <label htmlFor="file-upload" className="cursor-pointer block">
              <FileSpreadsheet className="mx-auto text-indigo-400 mb-2" size={36} />
              <div className="text-sm font-semibold text-white">
                {file ? file.name : 'Click to select or drag & drop dataset'}
              </div>
              <p className="text-xs text-gray-400 mt-1">
                {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Maximum file size: 50MB'}
              </p>
            </label>
          </div>

          {/* Optional Mapping Controls */}
          <div className="bg-black/30 p-4 rounded-xl border border-white/5 space-y-3">
            <div className="text-xs font-semibold uppercase text-gray-400 flex items-center gap-1.5">
              <Settings size={14} />
              Column Mapping & Parameters
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">Group Column</label>
                <input
                  type="text"
                  value={groupCol}
                  onChange={(e) => setGroupCol(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white font-mono"
                  placeholder="experiment_group"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">User ID Column</label>
                <input
                  type="text"
                  value={userCol}
                  onChange={(e) => setUserCol(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white font-mono"
                  placeholder="user_id"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Conversion Column</label>
                <input
                  type="text"
                  value={convCol}
                  onChange={(e) => setConvCol(e.target.value)}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white font-mono"
                  placeholder="conversion"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Significance Level (α)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.001"
                  max="0.20"
                  value={alpha}
                  onChange={(e) => setAlpha(parseFloat(e.target.value))}
                  className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white font-mono"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary text-sm"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary text-sm"
              disabled={!file || loading}
            >
              {loading ? 'Processing Pipeline...' : 'Run Full Pipeline'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
