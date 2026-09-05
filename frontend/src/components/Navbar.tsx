'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sparkles, Eye, Compass, Layers, RefreshCw, Zap } from 'lucide-react';
import { useCreateSnapshot } from '@/hooks/useGrowwLens';
import { DEMO_USER_ID } from '@/services/api';

export function Navbar() {
  const pathname = usePathname();
  const createSnapshotMutation = useCreateSnapshot();

  const handleQuickSnapshot = () => {
    createSnapshotMutation.mutate({ userId: DEMO_USER_ID, triggerType: 'manual' });
  };

  const navLinks = [
    { href: '/', label: 'Dashboard', icon: Eye },
    { href: '/watchlists', label: 'Watchlists', icon: Layers },
    { href: '/pulse', label: 'Market Pulse', icon: Compass },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/[0.08] bg-[#0a0b0e]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#00d09c] to-[#008f6b] p-0.5 flex items-center justify-center shadow-lg shadow-[#00d09c]/20 group-hover:shadow-[#00d09c]/40 transition-all duration-300">
              <div className="w-full h-full bg-[#0a0b0e] rounded-[10px] flex items-center justify-center">
                <Sparkles className="w-4 h-4 text-[#00d09c]" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  Groww Lens
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-medium tracking-wider uppercase rounded bg-[#00d09c]/10 text-[#00d09c] border border-[#00d09c]/20">
                  Memory
                </span>
              </div>
              <p className="text-[10px] text-slate-400 -mt-0.5 hidden sm:block">
                Your Market Memory
              </p>
            </div>
          </Link>

          {/* Navigation links */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-white/[0.08] text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-[#00d09c]' : 'text-slate-400'}`} />
                  {link.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right side controls */}
        <div className="flex items-center gap-3">
          {/* Live market pill */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            Memory Active
          </div>

          {/* Snapshot Trigger Button */}
          <button
            onClick={handleQuickSnapshot}
            disabled={createSnapshotMutation.isPending}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-white/[0.06] hover:bg-white/[0.1] border border-white/[0.08] text-slate-200 text-xs font-medium transition-all duration-200 active:scale-95 disabled:opacity-50"
            title="Save point-in-time market memory"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${createSnapshotMutation.isPending ? 'animate-spin text-[#00d09c]' : ''}`} />
            <span className="hidden sm:inline">
              {createSnapshotMutation.isPending ? 'Saving...' : 'Save Snapshot'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
