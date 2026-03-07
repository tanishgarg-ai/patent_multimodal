import React from 'react';
import { FileText, ExternalLink } from 'lucide-react';
import { useChatContext } from '../context/ChatContext';

export const PatentCard: React.FC<{ patent: any }> = ({ patent }) => {
  const { setSelectedPdfUrl } = useChatContext();

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-cyan-500/50 transition-colors group">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-sm font-semibold text-slate-200 line-clamp-2 pr-4" title={patent.title}>
          {patent.title || 'Untitled Patent'}
        </h3>
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-xs font-mono bg-slate-700 text-slate-300 px-2 py-1 rounded-md">
            {patent.patent_number || 'N/A'}
          </span>
          {patent.pdf_url && (
            <button
              onClick={() => setSelectedPdfUrl(patent.pdf_url)}
              className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-slate-700 rounded-md transition-colors opacity-0 group-hover:opacity-100"
              title="Open PDF"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
      
      {patent.similarity_score !== undefined && (
        <div className="flex items-center gap-2 mb-3">
          <div className="h-1.5 flex-1 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-cyan-500 rounded-full"
              style={{ width: `${Math.min(100, Math.max(0, patent.similarity_score * 100))}%` }}
            />
          </div>
          <span className="text-xs text-cyan-400 font-medium w-10 text-right">
            {(patent.similarity_score * 100).toFixed(0)}%
          </span>
        </div>
      )}

      <p className="text-xs text-slate-400 line-clamp-3 leading-relaxed">
        {patent.abstract || 'No abstract available.'}
      </p>
    </div>
  );
};
