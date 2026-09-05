'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Volume2,
  Sparkles,
  ChevronDown,
  Info,
  ExternalLink,
  Sliders,
} from 'lucide-react';
import type { MarketEvent } from '@/types';
import { ImpactScoreBadge } from './ImpactScoreBadge';

interface EventCardProps {
  event: MarketEvent;
  defaultExpanded?: boolean;
}

export function EventCard({ event, defaultExpanded }: EventCardProps) {
  const isHighImpact = event.impact_score >= 60;
  const isLowImpact = event.impact_score < 30;

  // Low impact items collapse by default as specified in product doc
  const [expanded, setExpanded] = useState(
    defaultExpanded !== undefined ? defaultExpanded : !isLowImpact
  );
  const [showBreakdown, setShowBreakdown] = useState(false);

  const isPricePositive = (event.price_change ?? 0) >= 0;

  // Metadata properties
  const meta = event.metadata ?? {};
  const snapshotPrice = meta.snapshot_price as number | undefined;
  const currentPrice = meta.current_price as number | undefined;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`rounded-xl border transition-all duration-200 overflow-hidden ${
        isHighImpact
          ? 'bg-[#151821]/90 border-rose-500/20 hover:border-rose-500/40 shadow-lg shadow-rose-950/20'
          : isLowImpact
          ? 'bg-[#101217]/60 border-white/[0.05] hover:border-white/[0.1] opacity-75 hover:opacity-100'
          : 'bg-[#14161f]/80 border-white/[0.08] hover:border-white/[0.15]'
      }`}
    >
      {/* Card Header / Summary Row */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="p-4 sm:p-5 flex items-center justify-between cursor-pointer select-none gap-4"
      >
        <div className="flex items-center gap-3.5 min-w-0">
          {/* Trend Icon Pill */}
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border ${
              isPricePositive
                ? 'bg-[#00d09c]/10 border-[#00d09c]/20 text-[#00d09c]'
                : 'bg-[#eb5b3c]/10 border-[#eb5b3c]/20 text-[#eb5b3c]'
            }`}
          >
            {isPricePositive ? (
              <TrendingUp className="w-5 h-5" />
            ) : (
              <TrendingDown className="w-5 h-5" />
            )}
          </div>

          {/* Symbol & Company Name */}
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white tracking-tight truncate">
                {event.symbol.replace('.NS', '')}
              </h3>
              <ImpactScoreBadge score={event.impact_score} size="sm" showLabel={false} />
            </div>
            <p className="text-xs text-slate-400 truncate">
              {event.company_name ?? event.symbol}
            </p>
          </div>
        </div>

        {/* Price & Volume Stats */}
        <div className="flex items-center gap-3 sm:gap-5 shrink-0">
          <div className="text-right">
            {event.price_change != null && (
              <div
                className={`text-sm font-semibold font-mono flex items-center justify-end gap-1 ${
                  isPricePositive ? 'text-[#00d09c]' : 'text-[#eb5b3c]'
                }`}
              >
                <span>{isPricePositive ? '+' : ''}{event.price_change.toFixed(2)}%</span>
              </div>
            )}
            {event.volume_ratio != null && event.volume_ratio > 1.2 && (
              <div className="text-[11px] font-mono text-slate-400 flex items-center justify-end gap-1">
                <Volume2 className="w-3 h-3 text-amber-400/80" />
                <span>{event.volume_ratio.toFixed(1)}× vol</span>
              </div>
            )}
          </div>

          {/* Collapse Arrow */}
          <div
            className={`w-7 h-7 rounded-lg bg-white/[0.04] border border-white/[0.06] flex items-center justify-center text-slate-400 transition-transform duration-200 ${
              expanded ? 'rotate-180 text-slate-200' : ''
            }`}
          >
            <ChevronDown className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Expanded Content Area */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-white/[0.06] px-4 pb-4 pt-3 sm:px-5 sm:pb-5 space-y-3.5"
          >
            {/* Event Summary */}
            <p className="text-sm text-slate-200 leading-relaxed font-medium">
              {event.summary}
            </p>

            {/* Price Delta Comparison Pill */}
            {snapshotPrice && currentPrice && (
              <div className="flex items-center gap-3 text-xs bg-white/[0.03] border border-white/[0.06] px-3.5 py-2 rounded-lg font-mono text-slate-300">
                <span className="text-slate-400">Last Seen:</span>
                <span className="text-slate-200 font-semibold">₹{snapshotPrice.toLocaleString('en-IN')}</span>
                <span className="text-slate-500">→</span>
                <span className="text-slate-400">Now:</span>
                <span className="text-white font-semibold">₹{currentPrice.toLocaleString('en-IN')}</span>
              </div>
            )}

            {/* AI "Why It Matters" Intelligence Box */}
            {event.explanation && (
              <div className="rounded-xl bg-gradient-to-br from-[#00d09c]/[0.08] via-transparent to-transparent border border-[#00d09c]/20 p-3.5 sm:p-4">
                <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-[#00d09c]">
                  <Sparkles className="w-3.5 h-3.5 animate-pulse" />
                  <span>Why It Matters</span>
                </div>
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                  {event.explanation}
                </p>
              </div>
            )}

            {/* Bottom Actions Bar */}
            <div className="flex items-center justify-between pt-1 text-xs text-slate-400">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowBreakdown(!showBreakdown);
                }}
                className="flex items-center gap-1.5 text-slate-400 hover:text-slate-200 transition-colors"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>{showBreakdown ? 'Hide Formula Breakdown' : 'Impact Score Breakdown'}</span>
              </button>

              <span className="text-[11px] text-slate-400">
                {new Date(event.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>

            {/* Impact Score Formula Breakdown Panel */}
            {showBreakdown && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-2 p-3 bg-black/40 rounded-lg border border-white/[0.06] text-xs space-y-2 font-mono"
              >
                <div className="text-slate-300 font-sans font-semibold text-[11px] uppercase tracking-wider text-slate-400">
                  Weighted Score Components (Total: {event.impact_score}/100)
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[11px]">
                  <div className="bg-white/[0.03] p-2 rounded border border-white/[0.04]">
                    <div className="text-slate-400 text-[10px]">Price (30%)</div>
                    <div className="text-slate-200 font-semibold">{event.price_change ? Math.abs(event.price_change).toFixed(1) + '%' : '—'}</div>
                  </div>
                  <div className="bg-white/[0.03] p-2 rounded border border-white/[0.04]">
                    <div className="text-slate-400 text-[10px]">Volume (25%)</div>
                    <div className="text-slate-200 font-semibold">{event.volume_ratio ? event.volume_ratio.toFixed(1) + '×' : '—'}</div>
                  </div>
                  <div className="bg-white/[0.03] p-2 rounded border border-white/[0.04]">
                    <div className="text-slate-400 text-[10px]">News (20%)</div>
                    <div className="text-slate-200 font-semibold">{meta.news ? 'Detected' : 'Routine'}</div>
                  </div>
                  <div className="bg-white/[0.03] p-2 rounded border border-white/[0.04]">
                    <div className="text-slate-400 text-[10px]">Volatility (15%)</div>
                    <div className="text-slate-200 font-semibold">{isHighImpact ? 'Elevated' : 'Normal'}</div>
                  </div>
                  <div className="bg-white/[0.03] p-2 rounded border border-white/[0.04]">
                    <div className="text-slate-400 text-[10px]">Watchlist (10%)</div>
                    <div className="text-[#00d09c] font-semibold">Priority</div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
