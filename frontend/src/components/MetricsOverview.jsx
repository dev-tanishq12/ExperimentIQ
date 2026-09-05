// frontend/src/components/MetricsOverview.jsx
import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, MousePointerClick, Clock, ArrowUpRight, ArrowDownRight } from 'lucide-react';

export default function MetricsOverview({ metrics, statisticalAnalysis }) {
  if (!metrics) return null;

  const conv = metrics.conversion_rate;
  const rev = metrics.revenue_per_user;
  const dur = metrics.session_duration;

  const convStats = statisticalAnalysis?.conversion || {};
  const revStats = statisticalAnalysis?.revenue || {};
  const durStats = statisticalAnalysis?.session_duration || {};

  const cards = [
    {
      title: 'Conversion Rate',
      icon: MousePointerClick,
      color: '#6366f1',
      metric: conv,
      stats: convStats,
      formatter: (v) => `${(v * 100).toFixed(2)}%`,
      absFormatter: (v) => `${(v * 100).toFixed(2)} pp`
    },
    {
      title: 'Revenue Per User',
      icon: DollarSign,
      color: '#10b981',
      metric: rev,
      stats: revStats,
      formatter: (v) => `$${Number(v).toFixed(2)}`,
      absFormatter: (v) => `$${Number(v).toFixed(2)}`
    },
    {
      title: 'Session Duration',
      icon: Clock,
      color: '#f59e0b',
      metric: dur,
      stats: durStats,
      formatter: (v) => `${Number(v).toFixed(1)}s`,
      absFormatter: (v) => `${Number(v).toFixed(1)}s`
    }
  ].filter(c => c.metric != null);

  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-4">
        <TrendingUp className="text-indigo-400" size={20} />
        <h2 className="text-sm font-bold tracking-wide uppercase text-gray-300">
          Member 3 • Metric Engine & Statistical Significance
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((c, i) => {
          const Icon = c.icon;
          const isPos = (c.metric.relative_lift_pct || 0) >= 0;
          const isSig = c.stats.is_significant;

          return (
            <div key={i} className="glass-card p-6 relative overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2.5">
                  <div 
                    className="p-2.5 rounded-xl border"
                    style={{ 
                      backgroundColor: `${c.color}20`, 
                      borderColor: `${c.color}40`,
                      color: c.color 
                    }}
                  >
                    <Icon size={18} />
                  </div>
                  <span className="text-base font-bold text-white">{c.title}</span>
                </div>

                {isSig ? (
                  <span className="badge badge-success text-xs">
                    p &lt; 0.05 (Sig)
                  </span>
                ) : (
                  <span className="badge badge-info text-xs">
                    p = {c.stats.p_value != null ? Number(c.stats.p_value).toFixed(3) : 'N/A'} (Not Sig)
                  </span>
                )}
              </div>

              {/* Lift Badge Highlight */}
              <div className="flex items-baseline justify-between my-4 bg-white/5 p-3 rounded-xl border border-white/5">
                <div>
                  <div className="text-xs text-gray-400 font-medium">Relative Lift</div>
                  <div className={`text-2xl font-black mt-0.5 flex items-center gap-1 ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {isPos ? <ArrowUpRight size={22} /> : <ArrowDownRight size={22} />}
                    {c.metric.relative_lift_pct > 0 ? '+' : ''}{c.metric.relative_lift_pct}%
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-xs text-gray-400 font-medium">Absolute Δ</div>
                  <div className="text-sm font-semibold font-mono text-gray-300 mt-1">
                    {c.absFormatter(c.metric.absolute_lift)}
                  </div>
                </div>
              </div>

              {/* Control vs Treatment Comparison */}
              <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white/10 text-xs sm:text-sm">
                <div>
                  <div className="text-gray-400 font-medium">Control</div>
                  <div className="text-base font-bold font-mono text-gray-200 mt-0.5">
                    {c.formatter(c.metric.control)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-gray-400 font-medium">Treatment</div>
                  <div className="text-base font-bold font-mono text-white mt-0.5">
                    {c.formatter(c.metric.treatment)}
                  </div>
                </div>
              </div>

              {/* 95% Confidence Interval if available */}
              {c.stats.confidence_interval && (
                <div className="mt-3 text-xs text-gray-400 bg-black/20 p-2 rounded-lg font-mono">
                  95% CI: [{c.stats.confidence_interval.lower}, {c.stats.confidence_interval.upper}]
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
