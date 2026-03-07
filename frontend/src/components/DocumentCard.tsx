import React from 'react';
import { File, Eye } from 'lucide-react';
import { Document, useChatContext } from '../context/ChatContext';

export const DocumentCard: React.FC<{ document: Document }> = ({ document }) => {
  const { setSelectedPdfUrl } = useChatContext();

  return (
    <div className="bg-slate-800 rounded-lg p-3 border border-slate-700 hover:border-cyan-500/50 transition-colors group">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="bg-slate-700 p-2 rounded-md shrink-0">
            <File className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-slate-200 truncate" title={document.filename}>
              {document.filename}
            </p>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-xs text-slate-400">Chunks: {document.chunks_added}</span>
              <span className="text-xs px-1.5 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20">
                {document.status}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={() => setSelectedPdfUrl(document.pdf_url)}
          className="p-1.5 text-slate-400 hover:text-cyan-400 hover:bg-slate-700 rounded-md transition-colors opacity-0 group-hover:opacity-100 shrink-0"
          title="View PDF"
        >
          <Eye className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
