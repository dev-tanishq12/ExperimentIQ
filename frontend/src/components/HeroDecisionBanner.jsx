// frontend/src/components/HeroDecisionBanner.jsx
import React, { useState } from 'react';
import { 
  Rocket, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowRight,
  ShieldCheck,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Target,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

export default function HeroDecisionBanner({ decision, metrics, expQuality }) {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  if (!decision) return null;

  const {
    decision: rec,
    confidence_pct = 85,
    reason = '',
    evidence = [],
    warnings = []
  } = decision;

  const themeConfig = {
    LAUNCH: {
      headline: "Ship It — We Recommend Launching",
      story: "The treatment created a clear, reliable positive lift. With healthy statistical power and balanced allocation, this feature is ready for your users.",
      nextStep: "Proceed with 100% rollout to production users. Monitor standard baseline telemetry for 48 hours post-launch.",
      badge: "🚀 Safe to Launch",
      badgeColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
      accentGlow: "from-emerald-500/20 via-teal-500/10 to-transparent",
      borderColor: "border-emerald-500/30",
      icon: Rocket,
      iconColor: "text-emerald-400"
    },
    'DO NOT LAUNCH': {
      headline: "Do Not Ship — Variant Degrades Experience",
      story: "Our analysis shows strong statistical evidence that the treatment performed worse than the control experience. Releasing it would harm key user metrics.",
      nextStep: "Retire this variant. Review user research, heatmaps, and funnel analytics to diagnose why users struggled.",
      badge: "❌ Do Not Launch",
      badgeColor: "text-rose-400 bg-rose-500/10 border-rose-500/30",
      accentGlow: "from-rose-500/20 via-pink-500/10 to-transparent",
      borderColor: "border-rose-500/30",
      icon: XCircle,
      iconColor: "text-rose-400"
    },
    'CONTINUE EXPERIMENT': {
      headline: "Keep Testing — Inconclusive Results",
      story: "The treatment shows directional promise, but we have not gathered enough user observations to rule out random coincidence with 95% confidence.",
      nextStep: "Allow the experiment to run longer. Check power requirements below for estimated sample size targets.",
      badge: "⏳ Continue Experiment",
      badgeColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
      accentGlow: "from-amber-500/20 via-orange-500/10 to-transparent",
      borderColor: "border-amber-500/30",
      icon: Clock,
      iconColor: "text-amber-400"
    },
    'INVESTIGATE DATA': {
      headline: "Hold On — Data Tracking Problem Detected",
      story: "We detected structural issues such as Sample Ratio Mismatch (SRM) or user cohort leakage. Making business decisions on this data is high risk.",
      nextStep: "Inspect your event logging, assignment service, and telemetry pipeline before trusting conversion or revenue calculations.",
      badge: "⚠️ Investigate Data",
      badgeColor: "text-purple-400 bg-purple-500/10 border-purple-500/30",
      accentGlow: "from-purple-500/20 via-indigo-500/10 to-transparent",
      borderColor: "border-purple-500/30",
      icon: AlertTriangle,
      iconColor: "text-purple-400"
    }
  }[rec] || {
    headline: rec,
    story: reason,
    nextStep: "Review experiment findings.",
    badge: rec,
    badgeColor: "text-sky-400 bg-sky-500/10 border-sky-500/30",
    accentGlow: "from-sky-500/20 to-transparent",
    borderColor: "border-sky-500/30",
    icon: HelpCircle,
    iconColor: "text-sky-400"
  };

  const Icon = themeConfig.icon;
  const convMetric = metrics?.conversion_rate;
  const relLift = convMetric?.relative_lift_pct || 0;
  const isPos = relLift >= 0;

  return (
    <div className={`human-card border ${themeConfig.borderColor} p-6 sm:p-8 mb-8 relative overflow-hidden bg-gradient-to-br ${themeConfig.accentGlow}`}>
      {/* Top Meta Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-2.5">
          <span className={`pill-badge border font-mono ${themeConfig.badgeColor}`}>
            <Icon size={14} className={themeConfig.iconColor} />
            {themeConfig.badge}
          </span>
          <span className="text-xs text-gray-400 font-medium">
            Analyzed by ExperimentIQ Decision Engine
          </span>
        </div>

        <div className="flex items-center gap-2 bg-black/40 px-3 py-1.5 rounded-full border border-white/10 text-xs">
          <span className="text-gray-400">Decision Confidence:</span>
          <span className="font-bold text-white font-mono">{confidence_pct}%</span>
        </div>
      </div>

      {/* Main Headline & Human Story */}
      <div className="max-w-4xl">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-extrabold text-white tracking-tight leading-tight">
          {themeConfig.headline}
        </h1>
        <p className="text-gray-300 text-sm sm:text-base mt-2.5 leading-relaxed font-normal">
          {themeConfig.story}
        </p>
      </div>

      {/* Key Takeaway Highlight Bar */}
      {convMetric && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-6 bg-black/30 backdrop-blur-md p-4 rounded-2xl border border-white/10">
          <div>
            <div className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Control Baseline</div>
            <div className="text-lg sm:text-xl font-bold text-white font-mono mt-0.5">
              {convMetric.control_pct}%
            </div>
            <div className="text-[11px] text-gray-400">Baseline conversion</div>
          </div>

          <div>
            <div className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Treatment Variant</div>
            <div className="text-lg sm:text-xl font-bold text-white font-mono mt-0.5">
              {convMetric.treatment_pct}%
            </div>
            <div className="text-[11px] text-gray-400">Observed conversion</div>
          </div>

          <div>
            <div className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Relative Impact</div>
            <div className={`text-lg sm:text-xl font-bold font-mono mt-0.5 flex items-center gap-1 ${isPos ? 'text-emerald-400' : 'text-rose-400'}`}>
              {isPos ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
              {relLift > 0 ? '+' : ''}{relLift}%
            </div>
            <div className="text-[11px] text-gray-400">
              {convMetric.absolute_lift != null ? `${(convMetric.absolute_lift * 100).toFixed(2)} pp absolute` : ''}
            </div>
          </div>

          <div>
            <div className="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Traffic Balance (SRM)</div>
            <div className="text-lg sm:text-xl font-bold text-white font-mono mt-0.5 flex items-center gap-1.5">
              {expQuality?.srm?.passed ? (
                <span className="text-emerald-400 flex items-center gap-1 text-sm sm:text-base font-bold">
                  <CheckCircle2 size={16} /> Balanced
                </span>
              ) : (
                <span className="text-rose-400 flex items-center gap-1 text-sm sm:text-base font-bold">
                  <AlertTriangle size={16} /> Imbalanced
                </span>
              )}
            </div>
            <div className="text-[11px] text-gray-400">Cohort distribution check</div>
          </div>
        </div>
      )}

      {/* Recommended Next Step Box */}
      <div className="bg-white/[0.04] p-4 rounded-xl border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400 mt-0.5">
            <Target size={18} />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-300 block">
              Suggested Next Step
            </span>
            <p className="text-xs sm:text-sm text-gray-200 mt-0.5">
              {themeConfig.nextStep}
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
          className="text-xs font-semibold text-gray-400 hover:text-white flex items-center gap-1 shrink-0 py-1 px-2.5 rounded-lg hover:bg-white/5"
        >
          <span>{showTechnicalDetails ? 'Hide technical signals' : 'Inspect technical signals'}</span>
          {showTechnicalDetails ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* Progressive Disclosure: Technical Evidence & Warnings */}
      {showTechnicalDetails && (
        <div className="mt-5 pt-5 border-t border-white/10 grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div>
            <div className="font-bold text-gray-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <CheckCircle2 size={14} className="text-emerald-400" />
              Verified Statistical Evidence
            </div>
            <ul className="space-y-1.5">
              {evidence.map((ev, i) => (
                <li key={i} className="text-gray-300 bg-black/20 p-2 rounded border border-white/5">
                  • {ev}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="font-bold text-gray-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <AlertTriangle size={14} className="text-amber-400" />
              Guardrail Checks & Risk Assessment
            </div>
            {warnings.length > 0 ? (
              <ul className="space-y-1.5">
                {warnings.map((w, i) => (
                  <li key={i} className="text-amber-300 bg-amber-500/10 p-2 rounded border border-amber-500/20">
                    ⚠️ {w}
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-emerald-300 bg-emerald-500/10 p-2 rounded border border-emerald-500/20">
                ✅ No critical sample anomalies or segment harms detected.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
