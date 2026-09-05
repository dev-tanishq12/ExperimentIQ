// frontend/src/components/ScenarioSelector.jsx
import React from 'react';
import { Play, UploadCloud, RefreshCw, Layers } from 'lucide-react';

export default function ScenarioSelector({ 
  currentScenario, 
  onSelectScenario, 
  onOpenUpload, 
  loading 
}) {
  const scenarios = [
    {
      id: 'scenario_a',
      name: 'Scenario A',
      badge: '🚀 LAUNCH',
      title: 'Winning Treatment',
      color: 'border-emerald-500/40 text-emerald-400 bg-emerald-500/10'
    },
    {
      id: 'scenario_b',
      name: 'Scenario B',
      badge: '⏳ CONTINUE',
      title: 'Underpowered Test',
      color: 'border-amber-500/40 text-amber-400 bg-amber-500/10'
    },
    {
      id: 'scenario_c',
      name: 'Scenario C',
      badge: '⚠️ INVESTIGATE',
      title: 'SRM & Leakage',
      color: 'border-purple-500/40 text-purple-400 bg-purple-500/10'
    },
    {
      id: 'scenario_d',
      name: 'Scenario D',
      badge: '❌ DO NOT LAUNCH',
      title: 'Harmful Variant',
      color: 'border-rose-500/40 text-rose-400 bg-rose-500/10'
    }
  ];

  return (
    <div className="glass-card p-4 sm:p-5 mb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <Layers className="text-indigo-400" size={20} />
          <div>
            <h2 className="text-sm font-bold tracking-wide uppercase text-gray-300">
              Evaluation Scenarios
            </h2>
            <p className="text-xs text-gray-400">
              Select a certified benchmark experiment or upload your own dataset.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {scenarios.map((sc) => {
            const isActive = currentScenario === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => onSelectScenario(sc.id)}
                disabled={loading}
                className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all flex items-center gap-2 ${
                  isActive
                    ? `${sc.color} ring-2 ring-indigo-500/50 scale-105 shadow-lg`
                    : 'bg-white/5 border-white/10 text-gray-300 hover:bg-white/10 hover:border-white/20'
                } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <span>{sc.badge}</span>
                <span className="hidden sm:inline">{sc.name}: {sc.title}</span>
              </button>
            );
          })}

          <button
            onClick={onOpenUpload}
            disabled={loading}
            className="btn-primary text-xs py-2 px-3.5 rounded-xl ml-auto md:ml-2"
          >
            <UploadCloud size={16} />
            <span>Upload Dataset</span>
          </button>
        </div>
      </div>
    </div>
  );
}
