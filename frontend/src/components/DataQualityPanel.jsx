// frontend/src/components/DataQualityPanel.jsx
import React from 'react';
import { Database, AlertOctagon, AlertTriangle, AlertCircle, CheckCircle, FileText } from 'lucide-react';

export default function DataQualityPanel({ qualityReport }) {
  if (!qualityReport) return null;

  const {
    file_info = {},
    issues = [],
    summary = {},
    quality_score = 1.0
  } = qualityReport;

  const scorePct = Math.round(quality_score * 100);

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'critical':
        return <span className="badge badge-danger">CRITICAL</span>;
      case 'high':
        return <span className="badge badge-danger">HIGH</span>;
      case 'medium':
        return <span className="badge badge-warning">MEDIUM</span>;
      default:
        return <span className="badge badge-info">LOW</span>;
    }
  };

  return (
    <div className="glass-card p-6 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <Database size={22} />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-indigo-400 font-semibold">
              Member 1 • Data Quality Module
            </div>
            <h2 className="text-xl font-bold text-white">
              Data Quality Profiling & Integrity Report
            </h2>
          </div>
        </div>

        {/* Quality Score Meter */}
        <div className="flex items-center gap-4 bg-black/30 px-5 py-3 rounded-xl border border-white/10">
          <div>
            <div className="text-xs text-gray-400 font-medium">Overall Quality Score</div>
            <div className="text-2xl font-black text-white">{scorePct}%</div>
          </div>
          <div className="w-24 bg-gray-800 h-3 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all duration-500 ${
                scorePct >= 80 ? 'bg-emerald-500' : scorePct >= 65 ? 'bg-amber-500' : 'bg-rose-500'
              }`}
              style={{ width: `${scorePct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Dataset Metadata Summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 my-6">
        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium flex items-center gap-1.5">
            <FileText size={14} className="text-indigo-400" />
            Total Rows
          </div>
          <div className="text-xl font-bold text-white mt-1">
            {file_info.rows ? file_info.rows.toLocaleString() : 'N/A'}
          </div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium flex items-center gap-1.5">
            <Database size={14} className="text-indigo-400" />
            Total Columns
          </div>
          <div className="text-xl font-bold text-white mt-1">
            {file_info.columns || 'N/A'}
          </div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium flex items-center gap-1.5">
            <AlertOctagon size={14} className="text-rose-400" />
            Critical / High Issues
          </div>
          <div className="text-xl font-bold text-rose-400 mt-1">
            {(summary.critical || 0) + (summary.high || 0)}
          </div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium flex items-center gap-1.5">
            <AlertTriangle size={14} className="text-amber-400" />
            Medium / Low Issues
          </div>
          <div className="text-xl font-bold text-amber-400 mt-1">
            {(summary.medium || 0) + (summary.low || 0)}
          </div>
        </div>
      </div>

      {/* Issues Table */}
      <div className="mt-6">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-300 mb-3">
          Detected Quality Anomalies ({issues.length})
        </h3>

        {issues.length > 0 ? (
          <div className="overflow-x-auto rounded-xl border border-white/10">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-white/5 text-gray-400 uppercase text-xs tracking-wider">
                <tr>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Column</th>
                  <th className="py-3 px-4">Issue Type</th>
                  <th className="py-3 px-4">Description</th>
                  <th className="py-3 px-4">Action Recommendation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-gray-300">
                {issues.map((issue, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 px-4">{getSeverityBadge(issue.severity)}</td>
                    <td className="py-3 px-4 font-mono font-medium text-indigo-300">
                      {issue.column || 'Dataset Wide'}
                    </td>
                    <td className="py-3 px-4 text-white font-medium capitalize">
                      {issue.type.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 px-4 text-gray-300">{issue.description}</td>
                    <td className="py-3 px-4 text-emerald-400 font-medium">
                      {issue.suggestion}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="bg-emerald-500/10 border border-emerald-500/20 p-4 rounded-xl text-emerald-300 flex items-center gap-3 text-sm">
            <CheckCircle size={18} />
            <span>Clean dataset: No structural issues or anomalies detected.</span>
          </div>
        )}
      </div>
    </div>
  );
}
