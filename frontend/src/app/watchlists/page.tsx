'use client';

import React from 'react';
import { Navbar } from '@/components/Navbar';
import { WatchlistManager } from '@/components/WatchlistManager';
import { Layers, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function WatchlistsPage() {
  return (
    <div className="min-h-screen bg-[#0a0b0e] text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Header Breadcrumb */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors mb-2"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Dashboard</span>
            </Link>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white flex items-center gap-2.5">
              <Layers className="w-7 h-7 text-[#00d09c]" />
              <span>Watchlist Management</span>
            </h1>
            <p className="text-sm text-slate-400 max-w-2xl">
              Organize equities by theme. Groww Lens automatically records snapshots of every stock in your active watchlists so you never miss a meaningful move.
            </p>
          </div>
        </div>

        {/* Manager Component */}
        <WatchlistManager />
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.06] bg-[#07080b] py-6 mt-12 text-center text-xs text-slate-400">
        <p>🔭 <strong>Groww Lens</strong> — Your Market Memory</p>
      </footer>
    </div>
  );
}
