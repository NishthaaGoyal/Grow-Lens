'use client';

import React from 'react';

interface ImpactScoreBadgeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export function ImpactScoreBadge({ score, size = 'md', showLabel = true }: ImpactScoreBadgeProps) {
  let tierColor = 'text-slate-400 bg-slate-500/10 border-slate-500/20';
  let tierLabel = 'Routine';
  let emoji = '💤';

  if (score >= 75) {
    tierColor = 'text-rose-400 bg-rose-500/10 border-rose-500/30 shadow-sm shadow-rose-500/10';
    tierLabel = 'Critical';
    emoji = '🚨';
  } else if (score >= 50) {
    tierColor = 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    tierLabel = 'High Impact';
    emoji = '⚠️';
  } else if (score >= 30) {
    tierColor = 'text-blue-400 bg-blue-500/10 border-blue-500/20';
    tierLabel = 'Moderate';
    emoji = '📌';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2 font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full font-mono border font-medium transition-all ${sizeClasses[size]} ${tierColor}`}
    >
      <span>{emoji}</span>
      <span>{score}</span>
      {showLabel && (
        <span className="text-[10px] font-sans font-normal opacity-80 uppercase tracking-wider pl-0.5">
          {tierLabel}
        </span>
      )}
    </span>
  );
}
