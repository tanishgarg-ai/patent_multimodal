import React from 'react';
import { X, FileText } from 'lucide-react';
import { useChatContext } from '../context/ChatContext';

export const PDFViewer = () => {
  const { selectedPdfUrl, setSelectedPdfUrl } = useChatContext();

  if (!selectedPdfUrl) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4 md:p-8">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-6xl h-full flex flex-col overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-800/50">
          <div className="flex items-center gap-3">
            <div className="bg-cyan-500/20 p-2 rounded-lg">
              <FileText className="w-5 h-5 text-cyan-400" />
            </div>
            <h3 className="text-lg font-semibold text-slate-200">Document Viewer</h3>
          </div>
          <button
            onClick={() => setSelectedPdfUrl(null)}
            className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-xl transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        <div className="flex-1 bg-slate-950">
          <iframe
            src={selectedPdfUrl}
            className="w-full h-full border-none"
            title="PDF Viewer"
          />
        </div>
      </div>
    </div>
  );
};
