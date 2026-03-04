import React from 'react';
import { motion } from 'motion/react';

interface NoveltyGaugeProps {
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
}

export const NoveltyGauge: React.FC<NoveltyGaugeProps> = ({ risk }) => {
  const getAngle = () => {
    switch (risk) {
      case 'LOW': return -60;
      case 'MEDIUM': return 0;
      case 'HIGH': return 60;
      default: return 0;
    }
  };

  const getColor = () => {
    switch (risk) {
      case 'LOW': return 'text-emerald-500';
      case 'MEDIUM': return 'text-amber-500';
      case 'HIGH': return 'text-red-500';
      default: return 'text-slate-500';
    }
  };

  const getBgColor = () => {
    switch (risk) {
      case 'LOW': return 'bg-emerald-500/10';
      case 'MEDIUM': return 'bg-amber-500/10';
      case 'HIGH': return 'bg-red-500/10';
      default: return 'bg-slate-500/10';
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center p-6">
      <svg width="200" height="120" viewBox="0 0 200 120" className="overflow-visible">
        {/* Background Arc */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="#1e293b"
          strokeWidth="12"
          strokeLinecap="round"
        />
        {/* Risk Zones */}
        <path d="M 20 100 A 80 80 0 0 1 73 30" fill="none" stroke="#10b981" strokeWidth="12" strokeOpacity="0.2" />
        <path d="M 73 30 A 80 80 0 0 1 127 30" fill="none" stroke="#f59e0b" strokeWidth="12" strokeOpacity="0.2" />
        <path d="M 127 30 A 80 80 0 0 1 180 100" fill="none" stroke="#ef4444" strokeWidth="12" strokeOpacity="0.2" />
        
        {/* Needle */}
        <motion.g
          initial={{ rotate: -90 }}
          animate={{ rotate: getAngle() }}
          transition={{ type: 'spring', stiffness: 50, damping: 10 }}
          style={{ originX: '100px', originY: '100px' }}
        >
          <line x1="100" y1="100" x2="100" y2="30" stroke="white" strokeWidth="3" strokeLinecap="round" />
          <circle cx="100" cy="100" r="6" fill="white" />
        </motion.g>
      </svg>
      
      <div className={cn("mt-4 px-6 py-2 rounded-full border border-current font-mono text-sm font-bold tracking-[0.2em]", getColor(), getBgColor())}>
        {risk} RISK
      </div>
    </div>
  );
};

import { cn } from '../lib/utils';
