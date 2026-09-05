'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Clock, AlertTriangle, CheckCircle2, BellRing, Sparkles, Filter } from 'lucide-react';
import type { WhileAwayStats } from '@/types';

interface WhileYouWereAwayHeroProps {
  stats: WhileAwayStats;
  selectedFilter: 'all' | 'high' | 'routine';
  onFilterChange: (filter: 'all' | 'high' | 'routine') => void;
  onSimulateAway?: () => void;
  isSimulating?: boolean;
}

export function WhileYouWereAwayHero({
  stats,
  selectedFilter,
  onFilterChange,
  onSimulateAway,
  isSimulating,
}: WhileYouWereAwayHeroProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-[#161a24] via-[#12141c] to-[#0d0e14] border border-white/[0.09] p-6 sm:p-8 shadow-2xl">
      {/* Background glow effects */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-[#00d09c]/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
      <div className="absolute bottom-0 left-10 w-72 h-72 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 space-y-6">
        {/* Top Tag & Time Away */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.05] border border-white/[0.08] text-xs font-medium text-slate-300">
            <Clock className="w-3.5 h-3.5 text-[#00d09c]" />
            <span>You were away for <strong className="text-white font-mono">{stats.hours_away} hours</strong></span>
          </div>

          {/* Quick Demo Simulator Button */}
          {onSimulateAway && (
            <button
              onClick={onSimulateAway}
              disabled={isSimulating}
              className="flex items-center gap-1.5 text-xs px-3 py-1 rounded-lg bg-[#00d09c]/10 hover:bg-[#00d09c]/20 border border-[#00d09c]/30 text-[#00d09c] font-medium transition-all duration-200 active:scale-95 disabled:opacity-50"
            >
              <Sparkles className={`w-3.5 h-3.5 ${isSimulating ? 'animate-spin' : ''}`} />
              <span>{isSimulating ? 'Simulating...' : 'Simulate 12h Away (Demo)'}</span>
            </button>
          )}
        </div>

        {/* Main Title & Key Proposition */}
        <div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
            <span>While You Were Away</span>
          </h1>
          <p className="mt-1.5 text-sm sm:text-base text-slate-400 max-w-2xl">
            Groww Lens compared your last market snapshot against current real-time data.
            Here is what meaningfully changed and why it matters.
          </p>
        </div>

        {/* Key Metrics Dashboard Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 pt-2">
          {/* Total Events */}
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
              <BellRing className="w-5 h-5" />
            </div>
            <div>
              <div className="text-2xl font-bold font-mono text-white">
                {stats.total_events}
              </div>
              <div className="text-xs text-slate-400 font-medium">Market Events Detected</div>
            </div>
          </div>

          {/* Attention Required */}
          <div className="bg-rose-500/[0.04] border border-rose-500/20 rounded-xl p-4 flex items-center gap-3.5 shadow-sm shadow-rose-950/30">
            <div className="w-11 h-11 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 flex items-center justify-center shrink-0">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-2xl font-bold font-mono text-rose-400">
                {stats.high_impact_events}
              </div>
              <div className="text-xs text-rose-200/80 font-medium">Require Your Attention</div>
            </div>
          </div>

          {/* Safe to Ignore / Routine */}
          <div className="bg-white/[0.03] border border-white/[0.06] rounded-xl p-4 flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <div>
              <div className="text-2xl font-bold font-mono text-slate-300">
                {stats.low_impact_events}
              </div>
              <div className="text-xs text-slate-400 font-medium">Can Safely Be Ignored</div>
            </div>
          </div>
        </div>

        {/* Filter Navigation Tabs */}
        <div className="pt-2 flex flex-wrap items-center gap-2 border-t border-white/[0.06]">
          <span className="text-xs font-medium text-slate-400 mr-1 hidden sm:inline flex items-center gap-1">
            <Filter className="w-3 h-3 text-slate-400" /> Filter:
          </span>
          <button
            onClick={() => onFilterChange('all')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedFilter === 'all'
                ? 'bg-white text-slate-900 font-semibold shadow'
                : 'bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]'
            }`}
          >
            All Events ({stats.total_events})
          </button>
          <button
            onClick={() => onFilterChange('high')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
              selectedFilter === 'high'
                ? 'bg-rose-500 text-white font-semibold shadow-lg shadow-rose-500/20'
                : 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 border border-rose-500/20'
            }`}
          >
            <span>🚨 Attention Required</span>
            <span className="px-1.5 py-0.2 bg-black/20 rounded-full font-mono text-[11px]">
              {stats.high_impact_events}
            </span>
          </button>
          <button
            onClick={() => onFilterChange('routine')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              selectedFilter === 'routine'
                ? 'bg-slate-700 text-white font-semibold'
                : 'bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]'
            }`}
          >
            💤 Routine Fluctuations ({stats.low_impact_events})
          </button>
        </div>
      </div>
    </div>
  );
}
