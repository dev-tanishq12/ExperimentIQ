// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { 
  Rocket, 
  Layers, 
  CheckCircle2, 
  AlertTriangle, 
  RefreshCw, 
  Sparkles, 
  Database, 
  Scale, 
  TrendingUp, 
  Users, 
  FileText,
  Download,
  Activity
} from 'lucide-react';

import HeroDecisionBanner from './components/HeroDecisionBanner';
import ScenarioSelector from './components/ScenarioSelector';
import DataQualityPanel from './components/DataQualityPanel';
import CleaningAssistantPanel from './components/CleaningAssistantPanel';
import ExperimentHealthCard from './components/ExperimentHealthCard';
import MetricsOverview from './components/MetricsOverview';
import PowerAnalysisCard from './components/PowerAnalysisCard';
import SegmentAnalysisExplorer from './components/SegmentAnalysisExplorer';
import FileUploadModal from './components/FileUploadModal';

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentScenario, setCurrentScenario] = useState('scenario_a');
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  // Load initial demo scenario
  useEffect(() => {
    loadScenario('scenario_a');
  }, []);

  const loadScenario = async (scenarioId) => {
    try {
      setLoading(true);
      setError(null);
      setCurrentScenario(scenarioId);

      const res = await fetch('/api/run-demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ demo_id: scenarioId })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Server responded with ${res.status}`);
      }

      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error("Pipeline run error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomUpload = async (formData) => {
    try {
      setLoading(true);
      setError(null);
      setIsUploadOpen(false);
      setCurrentScenario('custom_upload');

      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.error || `Upload failed with status ${res.status}`);
      }

      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadJsonReport = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `experimentiq_report_${currentScenario}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen text-gray-100 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-200/80 bg-white/80 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 via-indigo-500 to-orange-400 flex items-center justify-center shadow-sm">
              <Rocket size={18} className="text-white" />
            </div>
            <div>
              <div className="font-extrabold text-lg text-slate-900 tracking-tight">ExperimentIQ</div>
              <div className="text-[11px] text-slate-500 hidden sm:block">
                calmer decisions for smarter product teams
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={downloadJsonReport}
              disabled={!data || loading}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-sm disabled:opacity-50"
              title="Export complete execution report as JSON"
            >
              <Download size={14} />
              <span className="hidden sm:inline">Export</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 rounded-2xl border border-slate-200 bg-white/70 p-5 shadow-sm">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-[11px] uppercase tracking-[0.18em] font-bold text-violet-600">Experiment health</p>
              <h1 className="mt-1 text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                Clear decisions, without the noise.
              </h1>
            </div>
            <div className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700">
              Live analysis ready
            </div>
          </div>
        </div>

        {/* Scenario Quick Switcher */}
        <ScenarioSelector
          currentScenario={currentScenario}
          onSelectScenario={loadScenario}
          onOpenUpload={() => setIsUploadOpen(true)}
          loading={loading}
        />

        {/* Loading Overlay */}
        {loading && (
          <div className="glass-card p-12 mb-8 text-center flex flex-col items-center justify-center">
            <RefreshCw size={36} className="text-indigo-400 animate-spin mb-4" />
            <h3 className="text-lg font-bold text-white">Running 10-Step ExperimentIQ Pipeline...</h3>
            <p className="text-xs text-gray-400 mt-1 max-w-md">
              Profiling data quality • Remediating anomalies • Testing SRM • Computing hypothesis tests • Slicing segments • Synthesizing explainable decision
            </p>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 p-4 rounded-xl text-rose-200 mb-8 flex items-start gap-3">
            <AlertTriangle className="text-rose-400 shrink-0 mt-0.5" size={20} />
            <div>
              <div className="font-bold text-rose-400">Execution Error</div>
              <div className="text-sm mt-0.5">{error}</div>
            </div>
          </div>
        )}

        {/* Rendered Pipeline Results */}
        {!loading && data && (
          <div className="space-y-6">
            {/* 1. HERO RECOMMENDATION BANNER (Most Important Final Screen) */}
            <HeroDecisionBanner
              decision={data.decision}
              metrics={data.metrics}
              expQuality={data.experiment_quality}
            />

            {/* Navigation Filter Tabs */}
            <div className="mb-6 flex flex-wrap items-center gap-2 overflow-x-auto pb-1">
              {[
                { id: 'all', label: 'Overview' },
                { id: 'metrics', label: 'Metrics' },
                { id: 'segments', label: 'Segments' },
                { id: 'quality', label: 'Quality' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`tab-pill whitespace-nowrap ${
                    activeTab === tab.id ? 'active' : ''
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* 2. METRICS OVERVIEW & STATISTICAL SIGNIFICANCE */}
            {(activeTab === 'all' || activeTab === 'metrics') && (
              <>
                <MetricsOverview
                  metrics={data.metrics}
                  statisticalAnalysis={data.statistical_analysis}
                />

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  <ExperimentHealthCard experimentQuality={data.experiment_quality} />
                  <PowerAnalysisCard powerAnalysis={data.power_analysis} />
                </div>
              </>
            )}

            {/* 3. SEGMENT ANALYSIS EXPLORER (Member 4 Primary Module) */}
            {(activeTab === 'all' || activeTab === 'segments') && (
              <SegmentAnalysisExplorer segmentAnalysis={data.segment_analysis} />
            )}

            {/* 4. DATA QUALITY & CLEANING (Members 1 & 2) */}
            {(activeTab === 'all' || activeTab === 'quality') && (
              <>
                <DataQualityPanel qualityReport={data.quality_report} />
                <CleaningAssistantPanel
                  cleaningReport={data.cleaning_report}
                  validationReport={data.validation_report}
                />
              </>
            )}
          </div>
        )}
      </main>

      {/* File Upload Modal */}
      <FileUploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUpload={handleCustomUpload}
        loading={loading}
      />

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white/70 py-6 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto px-4">
          ExperimentIQ • built to help teams make calmer, clearer experiment decisions.
        </div>
      </footer>
    </div>
  );
}
