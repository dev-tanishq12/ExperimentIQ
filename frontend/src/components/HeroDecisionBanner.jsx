// frontend/src/components/HeroDecisionBanner.jsx
import React from 'react';
import { 
  Rocket, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  ShieldAlert, 
  TrendingUp, 
  Info,
  ChevronRight,
  Flame
} from 'lucide-react';

export default function HeroDecisionBanner({ decision, metrics, expQuality }) {
  if (!decision) return null;

  const {
    decision: rec,
    confidence_pct = 85,
    reason = '',
    evidence = [],
    warnings = [],
    summary = {}
  } = decision;

  const config = {
    LAUNCH: {
      icon: Rocket,
      title: 'LAUNCH VARIANT',
      subtitle: 'Treatment demonstrates positive, statistically sound impact with adequate power.',
      cardClass: 'decision-launch',
      badgeClass: 'badge-success',
      color: '#10b981',
      emoji: '🚀'
    },
    'DO NOT LAUNCH': {
      icon: XCircle,
      title: 'DO NOT LAUNCH',
      subtitle: 'Evidence indicates treatment significantly degrades key metrics or causes harm.',
      cardClass: 'decision-do_not_launch',
      badgeClass: 'badge-danger',
      color: '#ef4444',
      emoji: '❌'
    },
    'CONTINUE EXPERIMENT': {
      icon: Clock,
      title: 'CONTINUE EXPERIMENT',
      subtitle: 'Insufficient sample size or evidence to make a confident launch decision.',
      cardClass: 'decision-continue',
      badgeClass: 'badge-warning',
      color: '#f59e0b',
      emoji: '⏳'
    },
    'INVESTIGATE DATA': {
      icon: AlertTriangle,
      title: 'INVESTIGATE DATA',
      subtitle: 'Data quality defect, severe SRM, or cohort contamination detected.',
      cardClass: 'decision-investigate',
      badgeClass: 'badge-info',
      color: '#a855f7',
      emoji: '⚠️'
    }
  }[rec] || {
    icon: Info,
    title: rec,
    subtitle: 'Decision recommendation',
    cardClass: 'glass-card',
    badgeClass: 'badge-info',
    color: '#6366f1',
    emoji: '📊'
  };

  const Icon = config.icon;
  const convMetric = metrics?.conversion_rate;

  return (
    <div className={`glass-card ${config.cardClass} p-6 sm:p-8 mb-8 relative overflow-hidden`}>
      {/* Decorative corner glow */}
      <div 
        className="absolute -right-16 -top-16 w-48 h-48 rounded-full opacity-20 pointer-events-none blur-2xl"
        style={{ backgroundColor: config.color }}
      />

      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-white/10">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-3xl">{config.emoji}</span>
            <span className="text-xs font-semibold tracking-wider uppercase text-gray-400">
              Official Recommendation
            </span>
            <span className={`badge ${config.badgeClass}`}>
              {confidence_pct}% Confidence Score
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
            {config.title}
          </h1>
          <p className="text-gray-300 mt-2 text-base sm:text-lg max-w-3xl leading-relaxed">
            {reason}
          </p>
        </div>

        {/* Confidence Meter Badge */}
        <div className="flex lg:flex-col items-center lg:items-end justify-between bg-black/30 p-4 rounded-xl border border-white/10 min-w-[200px]">
          <span className="text-xs uppercase text-gray-400 font-medium">Confidence Level</span>
          <div className="text-3xl font-black mt-1" style={{ color: config.color }}>
            {confidence_pct}%
          </div>
          <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden mt-2">
            <div 
              className="h-full rounded-full transition-all duration-1000"
              style={{ width: `${confidence_pct}%`, backgroundColor: config.color }}
            />
          </div>
        </div>
      </div>

      {/* Conversion Metric Highlights if present */}
      {convMetric && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 my-6 bg-black/20 p-4 rounded-xl border border-white/5">
          <div>
            <div className="text-xs text-gray-400 font-medium">Control Conversion</div>
            <div className="text-xl font-bold text-white mt-1">
              {convMetric.control_pct != null ? `${convMetric.control_pct}%` : 'N/A'}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-400 font-medium">Treatment Conversion</div>
            <div className="text-xl font-bold text-white mt-1">
              {convMetric.treatment_pct != null ? `${convMetric.treatment_pct}%` : 'N/A'}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-400 font-medium">Absolute Difference</div>
            <div className={`text-xl font-bold mt-1 ${convMetric.absolute_lift >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {convMetric.absolute_lift != null ? `${(convMetric.absolute_lift * 100).toFixed(2)} pp` : 'N/A'}
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-400 font-medium">Relative Lift</div>
            <div className={`text-xl font-bold mt-1 ${convMetric.relative_lift_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {convMetric.relative_lift_pct != null ? `${convMetric.relative_lift_pct > 0 ? '+' : ''}${convMetric.relative_lift_pct}%` : 'N/A'}
            </div>
          </div>
        </div>
      )}

      {/* Supporting Evidence & Warnings Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
        {/* Evidence List */}
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-400" />
            Supporting Evidence & Statistical Signals
          </h3>
          <ul className="space-y-2">
            {evidence.map((ev, i) => (
              <li key={i} className="text-xs sm:text-sm text-gray-200 bg-white/5 p-2.5 rounded-lg border border-white/5 flex items-start gap-2">
                <ChevronRight size={15} className="text-indigo-400 shrink-0 mt-0.5" />
                <span>{ev}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Warnings & Risk Guardrails */}
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
            <AlertTriangle size={16} className="text-amber-400" />
            Guardrails, Warnings & Anomaly Checks
          </h3>
          {warnings.length > 0 ? (
            <ul className="space-y-2">
              {warnings.map((warn, i) => (
                <li key={i} className="text-xs sm:text-sm text-amber-200 bg-amber-500/10 p-2.5 rounded-lg border border-amber-500/20 flex items-start gap-2">
                  <AlertTriangle size={15} className="text-amber-400 shrink-0 mt-0.5" />
                  <span>{warn}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-xs sm:text-sm text-emerald-300 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20 flex items-center gap-2">
              <CheckCircle2 size={16} className="text-emerald-400" />
              No severe guardrail violations or harmful segment anomalies detected.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
