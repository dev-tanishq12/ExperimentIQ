// frontend/src/components/ScenarioSelector.jsx
import React from 'react';
import { UploadCloud, Sparkles } from 'lucide-react';

export default function ScenarioSelector({ 
  currentScenario, 
  onSelectScenario, 
  onOpenUpload, 
  loading 
}) {
  const scenarios = [
    {
      id: 'scenario_a',
      badge: '🚀 Launch',
      name: 'Winning Feature',
      subtitle: '+34.5% lift, high power',
      activeColor: 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300'
    },
    {
      id: 'scenario_b',
      badge: '⏳ Continue',
      name: 'Underpowered',
      subtitle: 'n=300, needs more data',
      activeColor: 'border-amber-500/50 bg-amber-500/10 text-amber-300'
    },
    {
      id: 'scenario_c',
      badge: '⚠️ Investigate',
      name: 'SRM Mismatch',
      subtitle: 'Tracking leak & imbalance',
      activeColor: 'border-purple-500/50 bg-purple-500/10 text-purple-300'
    },
    {
      id: 'scenario_d',
      badge: '❌ Reject',
      name: 'Harmful Variant',
      subtitle: '-30.6% drop in metric',
      activeColor: 'border-rose-500/50 bg-rose-500/10 text-rose-300'
    }
  ];

  return (
    <div className="mb-8 rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm sm:p-5">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Sparkles size={16} className="text-violet-500" />
            Explore Live Experiments
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Click any test scenario to see how ExperimentIQ analyzes real-world experiment situations:
          </p>
        </div>

        <button
          onClick={onOpenUpload}
          disabled={loading}
          className="self-start md:self-auto bg-slate-900 hover:bg-slate-800 text-white border border-slate-900 px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-sm disabled:opacity-60"
        >
          <UploadCloud size={16} className="text-violet-300" />
          <span>Upload Custom Dataset</span>
        </button>
      </div>

      {/* Scenario Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {scenarios.map((s) => {
          const isActive = currentScenario === s.id;
          return (
            <button
              key={s.id}
              onClick={() => onSelectScenario(s.id)}
              disabled={loading}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                isActive
                  ? `${s.activeColor} shadow-md ring-1 ring-slate-200`
                  : 'bg-slate-50 border-slate-200 hover:border-slate-300 hover:bg-white text-slate-700'
              } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center justify-between gap-1 mb-1">
                <span className="text-xs font-bold">{s.badge}</span>
                {isActive && (
                  <span className="w-2 h-2 rounded-full bg-violet-500 animate-ping" />
                )}
              </div>
              <div className="text-xs font-semibold text-slate-900 truncate">
                {s.name}
              </div>
              <div className="text-[11px] text-slate-500 truncate mt-0.5">
                {s.subtitle}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
