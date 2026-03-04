import React, { useState } from 'react';
import { Upload, Search, FileText, Lightbulb } from 'lucide-react';
import { motion } from 'motion/react';

interface InventionEditorProps {
  onAnalyze: (description: string, diagram?: File) => void;
  isAnalyzing: boolean;
}

export const InventionEditor: React.FC<InventionEditorProps> = ({ onAnalyze, isAnalyzing }) => {
  const [description, setDescription] = useState('');
  const [diagram, setDiagram] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setDiagram(file);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const wordCount = description.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="flex flex-col h-full bg-slate-900/50 border border-slate-800 rounded-xl p-4 overflow-hidden">
      <div className="flex items-center gap-2 mb-4 text-cyan-400">
        <Lightbulb size={20} />
        <h2 className="font-mono text-sm uppercase tracking-widest">Invention Workspace</h2>
      </div>

      <div className="flex-1 relative mb-4">
        <textarea
          className="w-full h-full bg-slate-950 border border-slate-800 rounded-lg p-4 text-slate-300 font-sans resize-none focus:outline-none focus:border-cyan-500/50 transition-colors"
          placeholder="Describe your invention in detail... e.g., A drone navigation system that uses LiDAR sensors and deep learning for real-time obstacle avoidance."
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div className="absolute bottom-3 right-3 text-xs text-slate-500 font-mono">
          {wordCount} words
        </div>
      </div>

      <div className="space-y-4">
        <div className="border-2 border-dashed border-slate-800 rounded-lg p-4 transition-colors hover:border-slate-700">
          <label className="flex flex-col items-center cursor-pointer">
            <Upload className="text-slate-500 mb-2" size={24} />
            <span className="text-xs text-slate-400 font-mono">Upload Schematic / Diagram</span>
            <input type="file" className="hidden" onChange={handleFileChange} accept="image/*" />
          </label>
          {preview && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-4 relative group"
            >
              <img src={preview} alt="Preview" className="w-full h-32 object-cover rounded border border-slate-700" />
              <button 
                onClick={() => { setDiagram(null); setPreview(null); }}
                className="absolute top-1 right-1 bg-red-500/80 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Search size={12} />
              </button>
            </motion.div>
          )}
        </div>

        <button
          onClick={() => onAnalyze(description, diagram || undefined)}
          disabled={isAnalyzing || description.length < 20}
          className={cn(
            "w-full py-3 rounded-lg font-mono text-sm uppercase tracking-widest flex items-center justify-center gap-2 transition-all",
            isAnalyzing 
              ? "bg-slate-800 text-slate-500 cursor-not-allowed" 
              : "bg-cyan-600 hover:bg-cyan-500 text-white shadow-lg shadow-cyan-900/20 active:scale-[0.98]"
          )}
        >
          {isAnalyzing ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
            >
              <Search size={18} />
            </motion.div>
          ) : (
            <Search size={18} />
          )}
          Investigate Prior Art
        </button>
      </div>
    </div>
  );
};

import { cn } from '../lib/utils';
