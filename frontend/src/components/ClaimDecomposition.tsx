import React from 'react';
import { motion } from 'motion/react';
import { CheckCircle2, AlertCircle } from 'lucide-react';

interface ClaimDecompositionProps {
  items: { component: string; isMatched: boolean }[];
}

export const ClaimDecomposition: React.FC<ClaimDecompositionProps> = ({ items }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {items.map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.05 }}
          className={cn(
            "p-3 rounded-lg border flex items-center justify-between gap-3",
            item.isMatched 
              ? "bg-red-500/5 border-red-500/20 text-red-200" 
              : "bg-emerald-500/5 border-emerald-500/20 text-emerald-200"
          )}
        >
          <span className="text-xs font-medium">{item.component}</span>
          {item.isMatched ? (
            <AlertCircle size={14} className="text-red-500 flex-shrink-0" />
          ) : (
            <CheckCircle2 size={14} className="text-emerald-500 flex-shrink-0" />
          )}
        </motion.div>
      ))}
    </div>
  );
};

import { cn } from '../lib/utils';
