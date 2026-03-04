import React, { useState } from 'react';
import { Patent } from '../types';
import { ChevronDown, ChevronUp, ExternalLink, FileText, ShieldAlert } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface PatentCardProps {
  patent: Patent;
}

export const PatentCard: React.FC<PatentCardProps> = ({ patent }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const chartData = [
    { name: 'Text', value: patent.similarityBreakdown.text },
    { name: 'Claim', value: patent.similarityBreakdown.claim },
    { name: 'Diagram', value: patent.similarityBreakdown.diagram },
    { name: 'Remaining', value: 3 - (patent.similarityBreakdown.text + patent.similarityBreakdown.claim + patent.similarityBreakdown.diagram) }
  ];

  const COLORS = ['#06b6d4', '#8b5cf6', '#f59e0b', '#1e293b'];

  return (
    <motion.div 
      layout
      className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-slate-700 transition-colors"
    >
      <div className="p-4 flex items-start gap-4">
        <div className="relative w-16 h-16 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={[{ value: patent.similarityScore }, { value: 1 - patent.similarityScore }]}
                innerRadius={20}
                outerRadius={30}
                paddingAngle={0}
                dataKey="value"
                startAngle={90}
                endAngle={-270}
              >
                <Cell fill={patent.similarityScore > 0.8 ? '#ef4444' : patent.similarityScore > 0.6 ? '#f59e0b' : '#10b981'} />
                <Cell fill="#1e293b" />
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center text-[10px] font-mono font-bold text-slate-300">
            {Math.round(patent.similarityScore * 100)}%
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn(
              "px-1.5 py-0.5 rounded text-[10px] font-mono uppercase",
              patent.source === 'Patent' ? "bg-blue-500/20 text-blue-400" : "bg-purple-500/20 text-purple-400"
            )}>
              {patent.source}
            </span>
            <span className="text-[10px] font-mono text-slate-500">{patent.year}</span>
          </div>
          <h3 className="text-sm font-medium text-slate-200 truncate">{patent.title}</h3>
          <p className="text-xs text-slate-500 font-mono mt-1">{patent.id}</p>
        </div>

        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 hover:bg-slate-800 rounded transition-colors text-slate-400"
        >
          {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
        </button>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-800"
          >
            <div className="p-4 space-y-4">
              <div>
                <h4 className="text-[10px] font-mono uppercase text-slate-500 mb-2 tracking-widest">Abstract</h4>
                <p className="text-xs text-slate-400 leading-relaxed">{patent.abstract}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-[10px] font-mono uppercase text-slate-500 mb-2 tracking-widest">Similarity Breakdown</h4>
                  <div className="space-y-2">
                    {[
                      { label: 'Text', val: patent.similarityBreakdown.text, color: 'bg-cyan-500' },
                      { label: 'Claims', val: patent.similarityBreakdown.claim, color: 'bg-violet-500' },
                      { label: 'Diagram', val: patent.similarityBreakdown.diagram, color: 'bg-amber-500' },
                    ].map((item) => (
                      <div key={item.label} className="space-y-1">
                        <div className="flex justify-between text-[10px] font-mono">
                          <span className="text-slate-500">{item.label}</span>
                          <span className="text-slate-300">{Math.round(item.val * 100)}%</span>
                        </div>
                        <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: `${item.val * 100}%` }}
                            className={cn("h-full", item.color)}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-[10px] font-mono uppercase text-slate-500 mb-2 tracking-widest">Key Claims</h4>
                  <ul className="space-y-2">
                    {patent.keyClaims.map((claim, i) => (
                      <li key={i} className="text-[10px] text-slate-400 flex gap-2">
                        <span className="text-cyan-500 font-mono">[{i+1}]</span>
                        <span className="line-clamp-2">{claim}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[10px] font-mono transition-colors">
                  <FileText size={12} /> Full Text
                </button>
                <button className="flex items-center gap-1 px-3 py-1.5 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 rounded text-[10px] font-mono transition-colors">
                  <ExternalLink size={12} /> Source
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

import { cn } from '../lib/utils';
