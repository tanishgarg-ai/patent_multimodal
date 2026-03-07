import React from 'react';
import { useChatContext } from '../context/ChatContext';
import { PatentCard } from './PatentCard';
import { AlertTriangle, CheckCircle, Info, Lightbulb, FileText } from 'lucide-react';

export const InsightPanel = () => {
  const { analysisResult, isAnalyzing } = useChatContext();

  if (isAnalyzing) {
    return (
      <div className="flex flex-col h-full bg-slate-900 p-6 items-center justify-center text-slate-500">
        <Lightbulb className="w-12 h-12 mb-4 animate-pulse text-cyan-500/50" />
        <p>Analyzing novelty and extracting insights...</p>
      </div>
    );
  }

  if (!analysisResult) {
    return (
      <div className="flex flex-col h-full bg-slate-900 p-6 items-center justify-center text-slate-500">
        <Info className="w-12 h-12 mb-4 text-slate-700" />
        <p className="text-center max-w-xs">
          Submit an invention description in the chat to see AI-generated novelty insights and prior art matches here.
        </p>
      </div>
    );
  }

  const riskLevel = analysisResult.novelty_assessment?.risk || 'UNKNOWN';
  
  const getRiskColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'LOW': return 'text-green-400 bg-green-500/10 border-green-500/20';
      case 'MEDIUM': return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
      case 'HIGH': return 'text-red-400 bg-red-500/10 border-red-500/20';
      default: return 'text-slate-400 bg-slate-800 border-slate-700';
    }
  };

  const getRiskIcon = (level: string) => {
    switch (level.toUpperCase()) {
      case 'LOW': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'MEDIUM': return <AlertTriangle className="w-5 h-5 text-orange-400" />;
      case 'HIGH': return <AlertTriangle className="w-5 h-5 text-red-400" />;
      default: return <Info className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 overflow-y-auto p-6 space-y-8">
      <div>
        <h2 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-cyan-400" />
          Novelty Risk Assessment
        </h2>
        <div className={`flex items-center gap-4 p-4 rounded-xl border ${getRiskColor(riskLevel)}`}>
          {getRiskIcon(riskLevel)}
          <div>
            <p className="text-sm font-medium uppercase tracking-wider">{riskLevel} RISK</p>
            <p className="text-xs opacity-80 mt-1">
              {analysisResult.novelty_assessment?.summary || 'Based on retrieved prior art and claim similarity.'}
            </p>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-cyan-400" />
          Prior Art Matches
        </h2>
        <div className="space-y-4">
          {analysisResult.patents && analysisResult.patents.length > 0 ? (
            analysisResult.patents.map((patent, idx) => (
              <PatentCard key={idx} patent={patent} />
            ))
          ) : (
            <p className="text-sm text-slate-500 italic">No similar patents found in the library.</p>
          )}
        </div>
      </div>
    </div>
  );
};
