import React from 'react';
import { ClaimMatch } from '../types';
import { motion } from 'motion/react';

interface ClaimComparisonTableProps {
  claims: ClaimMatch[];
}

export const ClaimComparisonTable: React.FC<ClaimComparisonTableProps> = ({ claims }) => {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-slate-800">
            <th className="py-3 px-4 text-[10px] font-mono uppercase text-slate-500 tracking-widest">Invention Component</th>
            <th className="py-3 px-4 text-[10px] font-mono uppercase text-slate-500 tracking-widest">Prior Art Match</th>
            <th className="py-3 px-4 text-[10px] font-mono uppercase text-slate-500 tracking-widest text-right">Similarity</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {claims.map((claim, i) => (
            <motion.tr 
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="hover:bg-slate-800/30 transition-colors"
            >
              <td className="py-3 px-4">
                <div className="text-xs text-slate-200 font-medium">{claim.component}</div>
              </td>
              <td className="py-3 px-4">
                <div className="text-[10px] text-cyan-400 font-mono">{claim.priorArtMatch}</div>
              </td>
              <td className="py-3 px-4 text-right">
                <div className={cn(
                  "text-xs font-mono font-bold",
                  claim.similarity > 0.8 ? "text-red-400" : claim.similarity > 0.6 ? "text-amber-400" : "text-emerald-400"
                )}>
                  {(claim.similarity * 100).toFixed(1)}%
                </div>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

import { cn } from '../lib/utils';
