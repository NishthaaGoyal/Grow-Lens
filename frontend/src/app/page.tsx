'use client';

import React, { useState } from 'react';
import { useWhileAway, useCreateSnapshot } from '@/hooks/useGrowwLens';
import { DEMO_USER_ID } from '@/services/api';
import { Navbar } from '@/components/Navbar';
import { WhileYouWereAwayHero } from '@/components/WhileYouWereAwayHero';
import { MarketPulseWidget } from '@/components/MarketPulseWidget';
import { EventCard } from '@/components/EventCard';
import { Sparkles, AlertCircle, RefreshCw, EyeOff, Layers } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { data: response, isLoading, isError, refetch } = useWhileAway(DEMO_USER_ID);
  const createSnapshotMutation = useCreateSnapshot();
  const [filter, setFilter] = useState<'all' | 'high' | 'routine'>('all');

  // Simulated "away" trigger: creates snapshot then refetches after simulated delay
  const handleSimulateAway = async () => {
    createSnapshotMutation.mutate(
      { userId: DEMO_USER_ID, triggerType: 'session_exit' },
      {
        onSuccess: () => {
          setTimeout(() => {
            refetch();
          }, 600);
        },
      }
    );
  };

  const stats = response?.stats ?? {
    hours_away: 12.0,
    total_events: 0,
    high_impact_events: 0,
    medium_impact_events: 0,
    low_impact_events: 0,
  };

  const allEvents = response?.events ?? [];

  // Filter logic
  const filteredEvents = allEvents.filter((ev) => {
    if (filter === 'high') return ev.impact_score >= 60;
    if (filter === 'routine') return ev.impact_score < 30;
    return true;
  });

  return (
    <div className="min-h-screen bg-[#0a0b0e] text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Loading State */}
        {isLoading && (
          <div className="space-y-6 animate-pulse">
            <div className="h-64 bg-white/[0.03] border border-white/[0.06] rounded-2xl"></div>
            <div className="h-32 bg-white/[0.03] border border-white/[0.06] rounded-2xl"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-24 bg-white/[0.03] border border-white/[0.06] rounded-xl"></div>
              ))}
            </div>
          </div>
        )}

        {/* Error Fallback */}
        {isError && (
          <div className="p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 text-center space-y-3">
            <AlertCircle className="w-8 h-8 text-rose-400 mx-auto" />
            <h3 className="text-base font-bold text-white">Could not load market memory</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Please ensure the backend server is running and database seed is initialized.
            </p>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-white/[0.08] hover:bg-white/[0.12] rounded-xl text-xs font-semibold text-white transition-all"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Loaded Content */}
        {!isLoading && !isError && (
          <>
            {/* 1. Feature 1 & 6: "While You Were Away" Hero */}
            <WhileYouWereAwayHero
              stats={stats}
              selectedFilter={filter}
              onFilterChange={setFilter}
              onSimulateAway={handleSimulateAway}
              isSimulating={createSnapshotMutation.isPending}
            />

            {/* 2. Feature 5: Daily Market Pulse */}
            <MarketPulseWidget pulse={response?.pulse} />

            {/* 3. Feature 6 & 7: Attention Feed (Card-based UI sorted by impact score) */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                    <span>Attention Feed</span>
                    <span className="text-xs font-normal text-slate-400">
                      (Ranked by Impact Score)
                    </span>
                  </h2>
                  <p className="text-xs text-slate-400">
                    High impact changes are highlighted. Routine fluctuations are collapsed to reduce noise.
                  </p>
                </div>

                <Link
                  href="/watchlists"
                  className="text-xs text-[#00d09c] hover:underline flex items-center gap-1"
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Manage Watchlists</span>
                </Link>
              </div>

              {filteredEvents.length > 0 ? (
                <div className="space-y-3">
                  {filteredEvents.map((event) => (
                    <EventCard
                      key={event.id}
                      event={event}
                      defaultExpanded={filter === 'routine' ? true : undefined}
                    />
                  ))}
                </div>
              ) : (
                <div className="text-center py-16 bg-[#12141c] border border-white/[0.06] rounded-2xl space-y-2">
                  <p className="text-sm font-medium text-slate-300">
                    No events match the selected filter ({filter}).
                  </p>
                  <p className="text-xs text-slate-500">
                    Select &quot;All Events&quot; above to review all market movements.
                  </p>
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.06] bg-[#07080b] py-6 mt-12 text-center text-xs text-slate-400">
        <p>🔭 <strong>Groww Lens</strong> — Transforming passive watchlists into actionable market memory.</p>
      </footer>
    </div>
  );
}
