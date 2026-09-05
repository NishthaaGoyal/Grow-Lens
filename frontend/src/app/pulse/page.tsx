'use client';

import React from 'react';
import { Navbar } from '@/components/Navbar';
import { SectorChart } from '@/components/SectorChart';
import { useMarketPulse } from '@/hooks/useGrowwLens';
import {
  Compass,
  Sparkles,
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Globe2,
  Zap,
  ShieldAlert,
} from 'lucide-react';
import Link from 'next/link';

export default function MarketPulsePage() {
  const { data: pulse, isLoading } = useMarketPulse();

  const isBullish = pulse?.market_mood === 'Bullish';

  return (
    <div className="min-h-screen bg-[#0a0b0e] text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Header Breadcrumb */}
        <div className="space-y-1">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Dashboard</span>
          </Link>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2.5">
                <Compass className="w-7 h-7 text-[#00d09c]" />
                <span>Daily Market Pulse</span>
              </h1>
              <p className="text-sm text-slate-400 max-w-2xl mt-1">
                Macroeconomic sentiment, top sector rotations, and Gemini-generated takeaways for Indian investors.
              </p>
            </div>

            {pulse?.market_mood && (
              <div
                className={`px-4 py-2 rounded-xl text-sm font-bold flex items-center gap-2 border ${
                  isBullish
                    ? 'bg-[#00d09c]/15 text-[#00d09c] border-[#00d09c]/30'
                    : 'bg-[#eb5b3c]/15 text-[#eb5b3c] border-[#eb5b3c]/30'
                }`}
              >
                {isBullish ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span>{pulse.market_mood} Outlook</span>
              </div>
            )}
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="space-y-6 animate-pulse">
            <div className="h-48 bg-white/[0.03] rounded-2xl border border-white/[0.06]"></div>
            <div className="h-80 bg-white/[0.03] rounded-2xl border border-white/[0.06]"></div>
          </div>
        )}

        {/* Loaded State */}
        {!isLoading && pulse && (
          <div className="space-y-6">
            {/* Top Insight Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="bg-[#12141c] border border-white/[0.06] rounded-2xl p-5 space-y-1">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-medium flex items-center gap-1.5">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Strongest Sector</span>
                </div>
                <div className="text-xl font-bold font-mono text-emerald-400 pt-1">
                  {pulse.strongest_sector ?? 'Auto & EV'}
                </div>
                <p className="text-[11px] text-slate-400">Leading momentum across indices</p>
              </div>

              <div className="bg-[#12141c] border border-white/[0.06] rounded-2xl p-5 space-y-1">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-medium flex items-center gap-1.5">
                  <TrendingDown className="w-3.5 h-3.5 text-rose-400" />
                  <span>Weakest Sector</span>
                </div>
                <div className="text-xl font-bold font-mono text-rose-400 pt-1">
                  {pulse.weakest_sector ?? 'Pharma'}
                </div>
                <p className="text-[11px] text-slate-400">Under mild profit booking</p>
              </div>

              <div className="bg-[#12141c] border border-white/[0.06] rounded-2xl p-5 space-y-1">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-medium flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-amber-400" />
                  <span>Top Market Theme</span>
                </div>
                <div className="text-xl font-bold font-mono text-amber-300 pt-1">
                  {pulse.top_theme ?? 'EV Momentum'}
                </div>
                <p className="text-[11px] text-slate-400">Driving retail participation</p>
              </div>

              <div className="bg-[#12141c] border border-white/[0.06] rounded-2xl p-5 space-y-1">
                <div className="text-xs uppercase tracking-wider text-slate-400 font-medium flex items-center gap-1.5">
                  <Globe2 className="w-3.5 h-3.5 text-blue-400" />
                  <span>Global Sentiment</span>
                </div>
                <div className="text-xl font-bold font-mono text-blue-400 pt-1">
                  {pulse.global_sentiment ?? 'Bullish'}
                </div>
                <p className="text-[11px] text-slate-400">Supported by Asian & US cues</p>
              </div>
            </div>

            {/* AI Narrative Section */}
            {pulse.ai_narrative && (
              <div className="rounded-2xl bg-gradient-to-br from-[#00d09c]/[0.08] via-[#12141c] to-[#0e1017] border border-[#00d09c]/25 p-6 sm:p-7 shadow-xl space-y-3">
                <div className="flex items-center gap-2 text-sm font-bold text-[#00d09c]">
                  <Sparkles className="w-4 h-4 animate-pulse" />
                  <span>Gemini AI Macro Narrative</span>
                </div>
                <p className="text-base text-slate-200 leading-relaxed">
                  {pulse.ai_narrative}
                </p>
              </div>
            )}

            {/* Sector Performance Chart */}
            <div className="bg-[#12141c] border border-white/[0.08] rounded-2xl p-6 space-y-4">
              <div>
                <h3 className="text-base font-bold text-white tracking-tight">
                  Sector Performance Comparison (% Daily Change)
                </h3>
                <p className="text-xs text-slate-400">
                  Relative performance across key sectors tracked by market memory.
                </p>
              </div>

              <SectorChart data={pulse.summary ? undefined : undefined} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.06] bg-[#07080b] py-6 mt-12 text-center text-xs text-slate-400">
        <p>🔭 <strong>Groww Lens</strong> — Daily Market Pulse</p>
      </footer>
    </div>
  );
}
