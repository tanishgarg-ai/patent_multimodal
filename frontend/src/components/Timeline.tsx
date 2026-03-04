import React from 'react';
import { Patent } from '../types';
import { motion } from 'motion/react';

interface TimelineProps {
  patents: Patent[];
}

export const Timeline: React.FC<TimelineProps> = ({ patents }) => {
  const sorted = [...patents].sort((a, b) => a.year - b.year);
  const minYear = sorted[0]?.year || 2000;
  const maxYear = sorted[sorted.length - 1]?.year || 2025;
  const range = maxYear - minYear || 1;

  return (
    <div className="relative py-8 px-4">
      <div className="absolute top-1/2 left-0 w-full h-px bg-slate-800 -translate-y-1/2" />
      
      <div className="relative flex justify-between items-center h-24">
        {sorted.map((p, i) => {
          const left = ((p.year - minYear) / range) * 100;
          return (
            <motion.div
              key={p.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="absolute flex flex-col items-center group"
              style={{ left: `${left}%`, transform: 'translateX(-50%)' }}
            >
              <div className="text-[10px] font-mono text-slate-500 mb-2 group-hover:text-cyan-400 transition-colors">
                {p.year}
              </div>
              <div className={cn(
                "w-3 h-3 rounded-full border-2 border-slate-950 z-10 transition-transform group-hover:scale-150",
                p.similarityScore > 0.8 ? "bg-red-500" : "bg-cyan-500"
              )} />
              <div className="absolute top-8 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900 border border-slate-700 p-2 rounded shadow-xl z-20 w-32 pointer-events-none">
                <div className="text-[10px] font-bold text-slate-200 truncate">{p.title}</div>
                <div className="text-[8px] font-mono text-slate-500">{p.id}</div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

import { cn } from '../lib/utils';
