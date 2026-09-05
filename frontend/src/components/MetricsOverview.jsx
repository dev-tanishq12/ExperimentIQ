// frontend/src/components/MetricsOverview.jsx
import React from 'react';
import {
  MousePointerClick,
  DollarSign,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  HelpCircle,
  CheckCircle2
} from 'lucide-react';

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
      color: '#38bdf8',
      metric: conv,
      stats: convStats,
      formatter: (v) => `${(v * 100).toFixed(2)}%`,
      absDiff: conv ? (conv.absolute_lift * 100).toFixed(2) + ' pp' : '',
      humanSummary: conv ? (
        conv.relative_lift_pct > 0
          ? `Treatment generated +${(conv.absolute_lift * 100).toFixed(1)} additional conversions per 100 visitors.`
          : `Treatment lost ${Math.abs(conv.absolute_lift * 100).toFixed(1)} conversions per 100 visitors.`
      ) : ''
    },
    {
      title: 'Revenue Per User',
      icon: DollarSign,
      color: '#34d399',
      metric: rev,
      stats: revStats,
      formatter: (v) => `$${Number(v).toFixed(2)}`,
      absDiff: rev ? (rev.absolute_lift > 0 ? '+$' : '-$') + Math.abs(rev.absolute_lift).toFixed(2) : '',
      humanSummary: rev ? (
        rev.relative_lift_pct > 0
          ? `Users spent an average of $${rev.absolute_lift.toFixed(2)} more with this variant.`
          : `Average spend per user decreased by $${Math.abs(rev.absolute_lift).toFixed(2)}.`
      ) : ''
    },
    {
      title: 'Session Duration',
      icon: Clock,
      color: '#fbbf24',
      metric: dur,
      stats: durStats,
      formatter: (v) => `${Number(v).toFixed(1)}s`,
      absDiff: dur ? (dur.absolute_lift > 0 ? '+' : '') + Number(dur.absolute_lift).toFixed(1) + 's' : '',
      humanSummary: dur ? (
        dur.absolute_lift > 0
          ? `Users spent ${Math.abs(dur.absolute_lift).toFixed(1)} seconds longer engaging with the variant.`
          : `Session length dropped by ${Math.abs(dur.absolute_lift).toFixed(1)} seconds.`
      ) : ''
    }
  ].filter(c => c.metric != null);

  return (
    <div className="mb-8">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight">
            Key Metric Performance
          </h2>
          <p className="text-xs text-gray-400">
            Control vs. treatment comparison across business metrics
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map((c, i) => {
          const Icon = c.icon;
          const isPos = (c.metric.relative_lift_pct || 0) >= 0;
          const isSig = c.stats.is_significant;

          return (
            <div key={i} className="human-card p-5 relative overflow-hidden flex flex-col justify-between">
              <div>
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${c.color}15`, color: c.color }}
                    >
                      <Icon size={16} />
                    </div>
                    <span className="text-sm font-bold text-white">{c.title}</span>
                  </div>

                  {isSig ? (
                    <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
                      <CheckCircle2 size={11} />
                      Significant
                    </span>
                  ) : (
                    <span className="text-[11px] font-medium text-gray-400 bg-white/5 border border-white/10 px-2 py-0.5 rounded-full">
                      Not Significant
                    </span>
                  )}
                </div>

                {/* Big Lift Number */}
                <div className="my-3">
                  <div className="flex items-baseline gap-2">
                    <div className={`text-3xl font-extrabold font-mono flex items-center ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {isPos ? <ArrowUpRight size={24} /> : <ArrowDownRight size={24} />}
                      {c.metric.relative_lift_pct > 0 ? '+' : ''}{c.metric.relative_lift_pct}%
                    </div>
                    <span className="text-xs text-gray-400 font-mono">
                      ({c.absDiff})
                    </span>
                  </div>

                  <p className="text-xs text-gray-300 mt-1 leading-snug">
                    {c.humanSummary}
                  </p>
                </div>

                {/* Control vs Treatment Comparison Pills */}
                <div className="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-white/5 text-xs">
                  <div className="bg-black/20 p-2.5 rounded-lg">
                    <div className="text-[10px] text-gray-400 uppercase font-semibold">Control</div>
                    <div className="text-sm font-bold font-mono text-gray-200 mt-0.5">
                      {c.formatter(c.metric.control)}
                    </div>
                  </div>
                  <div className="bg-black/20 p-2.5 rounded-lg">
                    <div className="text-[10px] text-gray-400 uppercase font-semibold">Treatment</div>
                    <div className="text-sm font-bold font-mono text-white mt-0.5">
                      {c.formatter(c.metric.treatment)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Confidence Interval footer */}
              {c.stats.confidence_interval && (
                <div className="mt-3 text-[11px] text-gray-400 flex items-center justify-between">
                  <span>95% Confidence Interval:</span>
                  <span className="font-mono text-gray-300">
                    [{c.stats.confidence_interval.lower}, {c.stats.confidence_interval.upper}]
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
