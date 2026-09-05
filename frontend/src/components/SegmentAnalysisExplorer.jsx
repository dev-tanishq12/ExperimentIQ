// frontend/src/components/SegmentAnalysisExplorer.jsx
import React, { useState } from 'react';
import { 
  Users, 
  Filter, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  BarChart2, 
  Info,
  CheckCircle2
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

export default function SegmentAnalysisExplorer({ segmentAnalysis }) {
  if (!segmentAnalysis) return null;

  const dimensions = segmentAnalysis.dimensions || {};
  const dimKeys = Object.keys(dimensions);

  const [selectedDim, setSelectedDim] = useState(dimKeys[0] || 'device');

  if (dimKeys.length === 0) {
    return (
      <div className="glass-card p-6 mb-8 text-center text-gray-400">
        <Users size={32} className="mx-auto mb-2 text-gray-500" />
        No categorical segmentation dimensions detected in this dataset.
      </div>
    );
  }

  const currentAnalysis = dimensions[selectedDim] || {};
  const segments = currentAnalysis.segments || [];
  const harmfulSegments = currentAnalysis.harmful_segments || [];
  const warnings = currentAnalysis.warnings || [];

  // Prepare data for Recharts
  const chartData = segments.map((s) => ({
    name: s.segment,
    Control: s.control_pct != null ? s.control_pct : (s.control_metric || 0),
    Treatment: s.treatment_pct != null ? s.treatment_pct : (s.treatment_metric || 0),
    lift: s.relative_lift_pct || 0,
    sample: s.total_n
  }));

  return (
    <div className="glass-card p-6 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-teal-500/20 text-teal-400 border border-teal-500/30">
            <Users size={22} />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-teal-400 font-semibold">
              Member 4 • Segment Analysis Engine
            </div>
            <h2 className="text-xl font-bold text-white">
              Multidimensional Segment Performance & Guardrails
            </h2>
          </div>
        </div>

        {/* Dimension Selector Tabs / Dropdown */}
        <div className="flex items-center gap-2">
          <Filter size={16} className="text-gray-400" />
          <span className="text-xs text-gray-400 font-medium">Dimension:</span>
          <div className="flex flex-wrap gap-1.5">
            {dimKeys.map((dim) => (
              <button
                key={dim}
                onClick={() => setSelectedDim(dim)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                  selectedDim === dim
                    ? 'bg-teal-500 text-white shadow-lg shadow-teal-500/25'
                    : 'bg-white/5 text-gray-400 hover:text-white hover:bg-white/10'
                }`}
              >
                {dim.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Harmful Segment Alert Banner */}
      {harmfulSegments.length > 0 && (
        <div className="my-6 bg-rose-500/10 border border-rose-500/30 p-4 rounded-xl text-rose-200">
          <div className="flex items-center gap-2 font-bold text-rose-400 text-sm mb-1">
            <AlertTriangle size={18} />
            Segment Degradation Detected in Dimension '{selectedDim}'!
          </div>
          <p className="text-xs sm:text-sm">
            The following credible user cohorts experience significant metric drop under the treatment:
          </p>
          <ul className="mt-2 space-y-1">
            {harmfulSegments.map((h, i) => (
              <li key={i} className="text-xs font-mono font-semibold">
                • {h.segment}: {h.lift_pct}% lift (n = {h.sample_size.toLocaleString()})
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recharts Visual Comparison */}
      <div className="my-6">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-400 mb-4 flex items-center gap-2">
          <BarChart2 size={16} className="text-teal-400" />
          Control vs. Treatment Conversion Rate by {selectedDim.replace(/_/g, ' ')}
        </h3>

        <div className="w-full h-64 sm:h-80 bg-black/20 p-4 rounded-xl border border-white/5">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
              <XAxis dataKey="name" stroke="#9ca3af" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <YAxis stroke="#9ca3af" tick={{ fill: '#9ca3af', fontSize: 12 }} unit="%" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#111827', 
                  borderColor: '#374151',
                  borderRadius: '8px',
                  color: '#f9fafb'
                }} 
              />
              <Legend wrapperStyle={{ paddingTop: '10px' }} />
              <Bar dataKey="Control" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Treatment" fill="#10b981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Segment Details Table */}
      <div className="mt-6">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-300 mb-3">
          Segment Level Breakdown ({segments.length} Cohorts)
        </h3>

        <div className="overflow-x-auto rounded-xl border border-white/10">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-white/5 text-gray-400 uppercase text-xs tracking-wider">
              <tr>
                <th className="py-3 px-4">Segment</th>
                <th className="py-3 px-4">Sample Size (Total)</th>
                <th className="py-3 px-4">Control Metric</th>
                <th className="py-3 px-4">Treatment Metric</th>
                <th className="py-3 px-4">Absolute Δ</th>
                <th className="py-3 px-4">Relative Lift</th>
                <th className="py-3 px-4">Significance</th>
                <th className="py-3 px-4">Status / Guardrails</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-gray-300">
              {segments.map((s, idx) => {
                const isPos = (s.relative_lift_pct || 0) >= 0;
                return (
                  <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 px-4 font-semibold text-white capitalize">
                      {s.segment}
                    </td>
                    <td className="py-3 px-4 font-mono">
                      {s.total_n?.toLocaleString() || 0}
                      <span className="text-gray-500 text-xs ml-1">
                        (Ctrl: {s.control_n}, Trt: {s.treatment_n})
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono">
                      {s.control_pct != null ? `${s.control_pct}%` : s.control_metric || '-'}
                    </td>
                    <td className="py-3 px-4 font-mono font-semibold text-white">
                      {s.treatment_pct != null ? `${s.treatment_pct}%` : s.treatment_metric || '-'}
                    </td>
                    <td className={`py-3 px-4 font-mono font-semibold ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {s.absolute_lift != null ? `${(s.absolute_lift * 100).toFixed(2)} pp` : '-'}
                    </td>
                    <td className={`py-3 px-4 font-mono font-bold ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {s.relative_lift_pct != null ? `${s.relative_lift_pct > 0 ? '+' : ''}${s.relative_lift_pct}%` : '-'}
                    </td>
                    <td className="py-3 px-4">
                      {s.is_significant ? (
                        <span className="badge badge-success text-xs">p &lt; 0.05</span>
                      ) : (
                        <span className="badge badge-info text-xs">
                          {s.p_value != null ? `p=${s.p_value}` : 'N/A'}
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      {s.is_small_sample ? (
                        <span className="badge badge-warning text-xs">
                          Small Sample (n &lt; 30)
                        </span>
                      ) : s.relative_lift_pct <= -10 ? (
                        <span className="badge badge-danger text-xs">
                          Harmful Segment
                        </span>
                      ) : (
                        <span className="badge badge-success text-xs">
                          Adequate Sample
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Warnings List */}
      {warnings.length > 0 && (
        <div className="mt-4 space-y-1">
          {warnings.map((w, i) => (
            <div key={i} className="text-xs text-amber-300 bg-amber-500/10 p-2.5 rounded-lg flex items-center gap-2">
              <Info size={14} className="shrink-0" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
