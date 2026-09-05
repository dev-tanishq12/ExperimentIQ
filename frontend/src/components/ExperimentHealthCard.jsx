// frontend/src/components/ExperimentHealthCard.jsx
import React from 'react';
import { Scale, Users, ShieldCheck, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function ExperimentHealthCard({ experimentQuality }) {
  if (!experimentQuality) return null;

  const {
    group_counts = {},
    srm = {},
    assignment_balance = {},
    quality_status = '✅ PASS'
  } = experimentQuality;

  const ctrlCount = group_counts.control || 0;
  const treatCount = group_counts.treatment || 0;
  const totalCount = group_counts.total || (ctrlCount + treatCount);

  const ctrlPct = totalCount > 0 ? ((ctrlCount / totalCount) * 100).toFixed(1) : '50.0';
  const treatPct = totalCount > 0 ? ((treatCount / totalCount) * 100).toFixed(1) : '50.0';

  const srmPassed = srm.passed !== false;

  return (
    <div className="glass-card p-6 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-blue-500/20 text-blue-400 border border-blue-500/30">
            <Scale size={22} />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-blue-400 font-semibold">
              Member 3 • Experiment Quality
            </div>
            <h2 className="text-xl font-bold text-white">
              Allocation Balance & Sample Ratio Mismatch (SRM)
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {srmPassed ? (
            <span className="badge badge-success text-sm py-1.5 px-3">
              <CheckCircle2 size={16} />
              SRM Check Passed (Balanced 50/50)
            </span>
          ) : (
            <span className="badge badge-danger text-sm py-1.5 px-3">
              <AlertTriangle size={16} />
              SRM Mismatch Detected!
            </span>
          )}
        </div>
      </div>

      {/* Group Distribution Visualizer */}
      <div className="my-6">
        <div className="flex justify-between text-xs sm:text-sm font-semibold mb-2">
          <span className="text-gray-300">Control: {ctrlCount.toLocaleString()} ({ctrlPct}%)</span>
          <span className="text-gray-300">Treatment: {treatCount.toLocaleString()} ({treatPct}%)</span>
        </div>

        {/* Proportional Split Bar */}
        <div className="w-full h-4 bg-gray-800 rounded-full overflow-hidden flex border border-white/10">
          <div 
            className="h-full bg-indigo-500 transition-all duration-700" 
            style={{ width: `${ctrlPct}%` }}
            title={`Control: ${ctrlPct}%`}
          />
          <div 
            className="h-full bg-emerald-500 transition-all duration-700" 
            style={{ width: `${treatPct}%` }}
            title={`Treatment: ${treatPct}%`}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1.5 font-mono">
          <span>Expected Split: 50%</span>
          <span>Expected Split: 50%</span>
        </div>
      </div>

      {/* Statistical SRM Diagnostic Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium">Chi-Square (χ²) Statistic</div>
          <div className="text-xl font-bold font-mono text-white mt-1">
            {srm.chi2_statistic != null ? srm.chi2_statistic : 'N/A'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Goodness-of-fit test</div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium">SRM p-value</div>
          <div className={`text-xl font-bold font-mono mt-1 ${srmPassed ? 'text-emerald-400' : 'text-rose-400'}`}>
            {srm.p_value != null ? srm.p_value : 'N/A'}
          </div>
          <div className="text-xs text-gray-500 mt-1">Alpha threshold = 0.05</div>
        </div>

        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
          <div className="text-xs text-gray-400 font-medium">Cohort Integrity</div>
          <div className="text-xl font-bold text-white mt-1 flex items-center gap-2">
            {assignment_balance.users_in_multiple_groups === 0 ? (
              <span className="text-emerald-400">0 Leaked Users</span>
            ) : (
              <span className="text-rose-400">{assignment_balance.users_in_multiple_groups} Contaminated</span>
            )}
          </div>
          <div className="text-xs text-gray-500 mt-1">Cross-group leakage check</div>
        </div>
      </div>
    </div>
  );
}
