'use client';

import React from 'react';
import Link from 'next/link';
import { Compass, Sparkles, TrendingUp, TrendingDown, ArrowRight, Activity } from 'lucide-react';
import type { MarketPulse } from '@/types';

interface MarketPulseWidgetProps {
  pulse?: MarketPulse | null;
  isLoading?: boolean;
}

export function MarketPulseWidget({ pulse, isLoading }: MarketPulseWidgetProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl bg-[#12141c] border border-white/[0.08] p-5 animate-pulse">
        <div className="h-5 w-36 bg-white/[0.08] rounded mb-3"></div>
        <div className="h-4 w-full bg-white/[0.05] rounded mb-2"></div>
        <div className="h-4 w-3/4 bg-white/[0.05] rounded"></div>
      </div>
    );
  }

  if (!pulse) return null;

  const isBullish = pulse.market_mood === 'Bullish';

  return (
    <div className="rounded-2xl bg-gradient-to-br from-[#151923] via-[#12141c] to-[#0f1117] border border-white/[0.08] p-5 sm:p-6 shadow-xl relative overflow-hidden">
      {/* Glow accent */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-[#00d09c]/10 rounded-full blur-2xl pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#00d09c]/10 border border-[#00d09c]/20 flex items-center justify-center text-[#00d09c]">
            <Compass className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Today's Market Pulse
            </h2>
            <p className="text-[11px] text-slate-400">
              AI macro context & daily market mood
            </p>
          </div>
        </div>

        {/* Mood Pill */}
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 border ${
            isBullish
              ? 'bg-[#00d09c]/15 text-[#00d09c] border-[#00d09c]/30'
              : 'bg-[#eb5b3c]/15 text-[#eb5b3c] border-[#eb5b3c]/30'
          }`}
        >
          {isBullish ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
          <span>{pulse.market_mood ?? 'Neutral'}</span>
        </span>
      </div>

      {/* 4 Telemetry Metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-4">
        <div className="bg-white/[0.03] border border-white/[0.05] p-2.5 rounded-xl">
          <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">Strongest Sector</div>
          <div className="text-xs sm:text-sm font-bold text-emerald-400 truncate mt-0.5">
            {pulse.strongest_sector ?? 'Auto & EV'}
          </div>
        </div>

        <div className="bg-white/[0.03] border border-white/[0.05] p-2.5 rounded-xl">
          <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">Weakest Sector</div>
          <div className="text-xs sm:text-sm font-bold text-rose-400 truncate mt-0.5">
            {pulse.weakest_sector ?? 'Pharma'}
          </div>
        </div>

        <div className="bg-white/[0.03] border border-white/[0.05] p-2.5 rounded-xl">
          <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">Top Theme</div>
          <div className="text-xs sm:text-sm font-bold text-amber-300 truncate mt-0.5">
            {pulse.top_theme ?? 'EV Stocks'}
          </div>
        </div>

        <div className="bg-white/[0.03] border border-white/[0.05] p-2.5 rounded-xl">
          <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">Global Sentiment</div>
          <div className="text-xs sm:text-sm font-bold text-blue-400 truncate mt-0.5">
            {pulse.global_sentiment ?? 'Bullish'}
          </div>
        </div>
      </div>

      {/* AI Narrative */}
      {pulse.ai_narrative && (
        <div className="bg-white/[0.02] border border-white/[0.04] rounded-xl p-3.5 text-xs text-slate-300 leading-relaxed flex items-start gap-2.5">
          <Sparkles className="w-4 h-4 text-[#00d09c] shrink-0 mt-0.5" />
          <p>{pulse.ai_narrative}</p>
        </div>
      )}

      {/* Link to Expanded Pulse */}
      <div className="mt-3.5 flex justify-end">
        <Link
          href="/pulse"
          className="inline-flex items-center gap-1.5 text-xs font-medium text-[#00d09c] hover:text-[#00d09c]/80 transition-colors"
        >
          <span>Explore Sector Deep Dive</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}
