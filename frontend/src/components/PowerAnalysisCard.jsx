// frontend/src/components/PowerAnalysisCard.jsx
import React from 'react';
import { Zap, AlertCircle, CheckCircle, Target } from 'lucide-react';

export default function PowerAnalysisCard({ powerAnalysis }) {
  if (!powerAnalysis) return null;

  const convPower = powerAnalysis.conversion;
  const revPower = powerAnalysis.revenue;

  const primaryPower = convPower || revPower;
  if (!primaryPower) return null;

  const currentN = primaryPower.current_sample_size || 0;
  const neededN = primaryPower.sample_size_needed || 0;
  const isPowered = primaryPower.is_adequately_powered;

  const progressPct = neededN > 0 ? Math.min(100, Math.round((currentN / neededN) * 100)) : 100;

  return (
    <div className="glass-card p-6 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <Zap size={22} />
          </div>
          <div>
            <div className="text-xs uppercase tracking-wider text-amber-400 font-semibold">
              Member 3 • Power & Sample Size Engine
            </div>
            <h2 className="text-xl font-bold text-white">
              Statistical Power & Sample Adequacy Analysis
            </h2>
          </div>
        </div>

        <div>
          {isPowered ? (
            <span className="badge badge-success text-sm py-1.5 px-3">
              <CheckCircle size={16} />
              Adequately Powered (Target ≥ 80%)
            </span>
          ) : (
            <span className="badge badge-warning text-sm py-1.5 px-3">
              <AlertCircle size={16} />
              Underpowered Experiment
            </span>
          )}
        </div>
      </div>

      <div className="my-6">
        <div className="flex justify-between text-xs sm:text-sm font-semibold mb-2">
          <span className="text-gray-300">
            Current Sample: <span className="text-white font-mono">{currentN.toLocaleString()}</span> users
          </span>
          <span className="text-gray-300">
            Required Sample: <span className="text-indigo-400 font-mono">{neededN.toLocaleString()}</span> users
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-3.5 bg-gray-800 rounded-full overflow-hidden border border-white/10">
          <div 
            className={`h-full rounded-full transition-all duration-700 ${
              isPowered ? 'bg-emerald-500' : 'bg-amber-500'
            }`}
            style={{ width: `${progressPct}%` }}
          />
        </div>

        <div className="flex justify-between text-xs text-gray-500 mt-1.5">
          <span>{progressPct}% of required sample size gathered</span>
          <span>Target Power: 80% (β = 0.20, α = 0.05)</span>
        </div>
      </div>

      <div className="bg-white/5 p-4 rounded-xl border border-white/5 text-xs sm:text-sm text-gray-300">
        <span className="font-semibold text-white">Interpretation: </span>
        {primaryPower.interpretation || (
          isPowered 
            ? 'The experiment has collected sufficient observations to reliably distinguish true effects from random fluctuations.'
            : `The test does not have enough statistical power to conclusively detect the observed effect size. We recommend continuing data collection until reaching approximately ${neededN.toLocaleString()} total observations.`
        )}
      </div>
    </div>
  );
}
