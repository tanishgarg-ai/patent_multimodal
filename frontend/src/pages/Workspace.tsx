import React from 'react';
import { DocumentUploader } from '../components/DocumentUploader';
import { RAGChat } from '../components/RAGChat';
import { InsightPanel } from '../components/InsightPanel';
import { PriorArtGraph } from '../components/PriorArtGraph';
import { PDFViewer } from '../components/PDFViewer';
import { ChatProvider } from '../context/ChatContext';
import { motion } from 'motion/react';
import { Microscope } from 'lucide-react';

export const Workspace = () => {
  return (
    <ChatProvider>
      <div className="flex flex-col h-screen bg-slate-950 text-slate-200 overflow-hidden font-sans">
        <header className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-slate-800 shrink-0 z-10">
          <div className="flex items-center gap-3">
            <div className="bg-cyan-500/20 p-2 rounded-lg">
              <Microscope className="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-slate-100 tracking-tight">Patent Prior-Art Investigation</h1>
              <p className="text-xs text-slate-400 font-mono">Workspace v1.0</p>
            </div>
          </div>
        </header>

        <main className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 grid grid-cols-1 md:grid-cols-3 min-h-0">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="h-full overflow-hidden"
            >
              <DocumentUploader />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="h-full overflow-hidden"
            >
              <RAGChat />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="h-full overflow-hidden"
            >
              <InsightPanel />
            </motion.div>
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="h-64 shrink-0"
          >
            <PriorArtGraph />
          </motion.div>
        </main>
        
        <PDFViewer />
      </div>
    </ChatProvider>
  );
};
