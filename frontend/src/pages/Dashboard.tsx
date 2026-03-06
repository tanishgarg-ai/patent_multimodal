import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { InventionEditor } from '../components/InventionEditor';
import { PatentCard } from '../components/PatentCard';
import { NoveltyGauge } from '../components/NoveltyGauge';
import { ClaimComparisonTable } from '../components/ClaimComparisonTable';
import { PriorArtGraph } from '../components/PriorArtGraph';
import { ClaimDecomposition } from '../components/ClaimDecomposition';
import { Timeline } from '../components/Timeline';
import { usePatentAnalysis } from '../hooks/usePatentAnalysis';
import {
  Search,
  Database,
  Cpu,
  Network,
  X,
  Info,
  History,
  Layers,
  Activity
} from 'lucide-react';
import { Patent } from '../types';

export const Dashboard: React.FC = () => {
  const { isAnalyzing, results, error, runAnalysis, step } = usePatentAnalysis();
  const [selectedPatent, setSelectedPatent] = useState<Patent | null>(null);

  const handleNodeClick = (id: string) => {
    const patent = results?.patents.find(p => p.id === id) || results?.papers.find(p => p.id === id);
    if (patent) setSelectedPatent(patent);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-cyan-500/30">
      {/* Header */}
      <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-cyan-600 rounded flex items-center justify-center shadow-lg shadow-cyan-900/40">
            <Database size={18} className="text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">PATENT<span className="text-cyan-500">INVESTIGATOR</span></h1>
            <p className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">Prior-Art Intelligence Workstation v2.4</p>
          </div>
        </div>
        <div className="flex items-center gap-6 text-[10px] font-mono text-slate-500 uppercase tracking-widest">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            System Online
          </div>
          <div>User: Examiner_742</div>
        </div>
      </header>

      <main className="p-6 space-y-6">
        {/* Top 3-Panel Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-320px)] min-h-[600px]">
          {/* Panel 1: Invention Input */}
          <div className="lg:col-span-3 h-full">
            <InventionEditor onAnalyze={runAnalysis} isAnalyzing={isAnalyzing} />
          </div>

          {/* Panel 2: Prior Art Results */}
          <div className="lg:col-span-5 h-full flex flex-col bg-slate-900/30 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
              <div className="flex items-center gap-2 text-cyan-400">
                <Database size={16} />
                <h2 className="font-mono text-xs uppercase tracking-widest">Discovery Results</h2>
              </div>
              {results && (
                <div className="text-[10px] font-mono text-slate-500">
                  {results.patents.length + results.papers.length} matches found
                </div>
              )}
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
              {!results && !isAnalyzing && !error && (
                <div className="h-full flex flex-col items-center justify-center text-slate-600 opacity-50">
                  <Search size={48} strokeWidth={1} className="mb-4" />
                  <p className="text-sm font-mono">Awaiting invention analysis...</p>
                </div>
              )}

              {error && (
                <div className="h-full flex flex-col items-center justify-center text-red-500 opacity-80">
                  <X size={48} strokeWidth={1} className="mb-4" />
                  <p className="text-sm font-mono">{error}</p>
                </div>
              )}

              {isAnalyzing && (
                <div className="h-full flex flex-col items-center justify-center">
                  <div className="relative w-24 h-24 mb-6">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                      className="absolute inset-0 border-2 border-cyan-500/20 rounded-full"
                    />
                    <motion.div
                      animate={{ rotate: -360 }}
                      transition={{ repeat: Infinity, duration: 3, ease: "linear" }}
                      className="absolute inset-2 border-2 border-cyan-500/40 border-t-cyan-500 rounded-full"
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Cpu size={24} className="text-cyan-500" />
                    </div>
                  </div>
                  <p className="text-sm font-mono text-cyan-400 animate-pulse">{step}</p>
                </div>
              )}

              {results && (
                <>
                  {results.patents.map(p => <PatentCard key={p.id} patent={p} />)}
                  {results.papers.map(p => <PatentCard key={p.id} patent={p} />)}
                </>
              )}
            </div>
          </div>

          {/* Panel 3: Insight AI */}
          <div className="lg:col-span-4 h-full flex flex-col bg-slate-900/30 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center gap-2 text-amber-400 bg-slate-900/50">
              <Cpu size={16} />
              <h2 className="font-mono text-xs uppercase tracking-widest">Novelty Assessment</h2>
            </div>
            <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
              {!results && !isAnalyzing && (
                <div className="h-full flex flex-col items-center justify-center text-slate-600 opacity-50">
                  <Activity size={48} strokeWidth={1} className="mb-4" />
                  <p className="text-sm font-mono">Awaiting intelligence feed...</p>
                </div>
              )}

              {results && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-8"
                >
                  <section>
                    <h3 className="text-[10px] font-mono uppercase text-slate-500 mb-4 tracking-widest flex items-center gap-2">
                      <Activity size={12} /> Risk Index
                    </h3>
                    <NoveltyGauge risk={results.noveltyAssessment.riskLevel} />
                    <p className="mt-4 text-xs text-slate-400 leading-relaxed italic border-l-2 border-slate-800 pl-4">
                      "{results.noveltyAssessment.explanation}"
                    </p>
                  </section>

                  <section>
                    <h3 className="text-[10px] font-mono uppercase text-slate-500 mb-4 tracking-widest flex items-center gap-2">
                      <Layers size={12} /> Claim Decomposition
                    </h3>
                    <ClaimDecomposition items={results.noveltyAssessment.decomposition} />
                  </section>

                  <section>
                    <h3 className="text-[10px] font-mono uppercase text-slate-500 mb-4 tracking-widest flex items-center gap-2">
                      <Info size={12} /> Claim Comparison
                    </h3>
                    <ClaimComparisonTable claims={results.noveltyAssessment.claimComparison} />
                  </section>
                </motion.div>
              )}
            </div>
          </div>
        </div>

        {/* Bottom Panel: Graph & Timeline */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-8 h-[400px] flex flex-col bg-slate-900/30 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center gap-2 text-cyan-400 bg-slate-900/50">
              <Network size={16} />
              <h2 className="font-mono text-xs uppercase tracking-widest">Prior Art Relationship Graph</h2>
            </div>
            <div className="flex-1">
              {results ? (
                <PriorArtGraph data={results.graphData} onNodeClick={handleNodeClick} />
              ) : (
                <div className="h-full flex items-center justify-center text-slate-700 font-mono text-sm">
                  Graph visualization offline
                </div>
              )}
            </div>
          </div>

          <div className="lg:col-span-4 h-[400px] flex flex-col bg-slate-900/30 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center gap-2 text-cyan-400 bg-slate-900/50">
              <History size={16} />
              <h2 className="font-mono text-xs uppercase tracking-widest">Prior Art Timeline</h2>
            </div>
            <div className="flex-1 p-4">
              {results ? (
                <Timeline patents={[...results.patents, ...results.papers]} />
              ) : (
                <div className="h-full flex items-center justify-center text-slate-700 font-mono text-sm">
                  Timeline data unavailable
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Detail Drawer */}
      <AnimatePresence>
        {selectedPatent && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedPatent(null)}
              className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-[60]"
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed top-0 right-0 h-full w-full max-w-md bg-slate-900 border-l border-slate-800 z-[70] shadow-2xl p-6 overflow-y-auto custom-scrollbar"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="px-2 py-1 bg-cyan-500/20 text-cyan-400 rounded text-[10px] font-mono uppercase">
                  {selectedPatent.source} Detail
                </div>
                <button
                  onClick={() => setSelectedPatent(null)}
                  className="p-2 hover:bg-slate-800 rounded-full transition-colors text-slate-400"
                >
                  <X size={20} />
                </button>
              </div>

              <h2 className="text-xl font-bold text-slate-100 mb-2">{selectedPatent.title}</h2>
              <p className="text-sm font-mono text-slate-500 mb-6">{selectedPatent.id} • {selectedPatent.filingDate}</p>

              <div className="space-y-8">
                <section>
                  <h3 className="text-[10px] font-mono uppercase text-slate-500 mb-3 tracking-widest">Abstract</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">{selectedPatent.abstract}</p>
                </section>

                <section>
                  <h3 className="text-[10px] font-mono uppercase text-slate-500 mb-3 tracking-widest">Similarity Explanation</h3>
                  <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-sm text-slate-400">
                    The technical overlap in {selectedPatent.similarityBreakdown.claim > 0.8 ? 'claims' : 'description'} suggests a high risk of non-novelty. Specifically, the implementation of LiDAR-based SLAM matches the disclosed methods in this {selectedPatent.source.toLowerCase()}.
                  </div>
                </section>

                <section>
                  <h3 className="text-[10px] font-mono uppercase text-slate-500 mb-3 tracking-widest">Top Claims</h3>
                  <div className="space-y-3">
                    {selectedPatent.keyClaims.map((claim, i) => (
                      <div key={i} className="p-3 bg-slate-950/50 rounded border border-slate-800/50 text-xs text-slate-400">
                        <span className="text-cyan-500 font-mono mr-2">CLAIM {i + 1}:</span>
                        {claim}
                      </div>
                    ))}
                  </div>
                </section>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #1e293b;
          border-radius: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #334155;
        }
      `}</style>
    </div>
  );
};
