// frontend/src/components/CleaningAssistantPanel.jsx
import React from 'react';
import { Sparkles, CheckCheck, RefreshCw, Scissors, ArrowRight, ShieldCheck } from 'lucide-react';

export default function CleaningAssistantPanel({ cleaningReport, validationReport }) {
  if (!cleaningReport && !validationReport) return null;

  const actions = cleaningReport?.cleaning_actions || [];
  const validation = validationReport || cleaningReport?.validation || {};
  const actionsSummary = cleaningReport?.actions_summary || {};

  const origMissing = validation.missing_values?.original || 0;
  const cleanedMissing = validation.missing_values?.cleaned || 0;
  const missingFixed = validation.missing_values?.fixed || (origMissing - cleanedMissing);

  const origDuplicates = validation.duplicates?.original || 0;
  const removedDuplicates = validation.duplicates?.removed || origDuplicates;

  return (
    <div className="glass-card p-6 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30">
            <Sparkles size={22} />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-purple-400 font-semibold">
              Member 2 • Intelligent Cleaning Assistant
            </div>
            <h2 className="text-xl font-bold text-white">
              Automated Data Cleaning & Validation Audit
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="badge badge-success">
            <ShieldCheck size={14} />
            Data Cleaned & Validated
          </span>
        </div>
      </div>

      {/* Validation Stats Comparison */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 my-6">
        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium">Original vs Cleaned Rows</div>
          <div className="text-lg font-bold text-white mt-1 flex items-center gap-2">
            <span>{validation.original_shape?.rows?.toLocaleString() || '-'}</span>
            <ArrowRight size={14} className="text-indigo-400" />
            <span className="text-emerald-400">{validation.cleaned_shape?.rows?.toLocaleString() || '-'}</span>
          </div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium">Missing Values Remediated</div>
          <div className="text-lg font-bold text-emerald-400 mt-1">
            {missingFixed > 0 ? `+${missingFixed.toLocaleString()}` : '0'}
          </div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium">Duplicates Purged</div>
          <div className="text-lg font-bold text-white mt-1">
            {removedDuplicates.toLocaleString()}
          </div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium">Cleaning Actions Applied</div>
          <div className="text-lg font-bold text-indigo-400 mt-1">
            {actions.length}
          </div>
        </div>
      </div>

      {/* Cleaning Actions Audit Trail */}
      {actions.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-300 mb-3">
            Cleaning Actions Applied ({actions.length})
          </h3>
          <div className="overflow-x-auto rounded-xl border border-white/10">
            <table className="w-full text-left text-xs sm:text-sm">
              <thead className="bg-white/5 text-gray-400 uppercase text-xs tracking-wider">
                <tr>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Target Column</th>
                  <th className="py-3 px-4">Issue Resolved</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Transformation Applied</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-gray-300">
                {actions.map((act, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-purple-300 capitalize">
                      {act.action?.replace(/_/g, ' ') || 'Action'}
                    </td>
                    <td className="py-3 px-4 font-mono text-gray-300">
                      {act.column || 'Cohort Wide'}
                    </td>
                    <td className="py-3 px-4 capitalize">
                      {act.issue_type?.replace(/_/g, ' ')}
                    </td>
                    <td className="py-3 px-4">
                      <span className="badge badge-info">
                        {Math.round((act.confidence || 0.85) * 100)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-300 text-xs sm:text-sm">
                      {act.explanation}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
