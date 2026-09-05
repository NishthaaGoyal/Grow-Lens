'use client';

import React, { useState } from 'react';
import { Plus, Trash2, Layers, Check, TrendingUp, TrendingDown, Activity, AlertCircle } from 'lucide-react';
import {
  useWatchlists,
  useWatchlistStocks,
  useCreateWatchlist,
  useDeleteWatchlist,
  useAddStock,
  useRemoveStock,
} from '@/hooks/useGrowwLens';
import { DEMO_USER_ID } from '@/services/api';

const POPULAR_SUGGESTIONS = [
  { symbol: 'TATAMOTORS.NS', name: 'Tata Motors Limited', sector: 'Auto' },
  { symbol: 'INFY.NS', name: 'Infosys Limited', sector: 'IT' },
  { symbol: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'IT' },
  { symbol: 'M&M.NS', name: 'Mahindra & Mahindra', sector: 'Auto' },
  { symbol: 'OLECTRA.NS', name: 'Olectra Greentech', sector: 'EV' },
  { symbol: 'WIPRO.NS', name: 'Wipro Limited', sector: 'IT' },
  { symbol: 'HDFCBANK.NS', name: 'HDFC Bank Limited', sector: 'Banking' },
  { symbol: 'RELIANCE.NS', name: 'Reliance Industries', sector: 'Energy' },
];

function formatVolume(vol?: number): string {
  if (!vol) return '—';
  if (vol >= 10_000_000) return `${(vol / 10_000_000).toFixed(2)}Cr`;
  if (vol >= 100_000) return `${(vol / 100_000).toFixed(2)}L`;
  if (vol >= 1_000) return `${(vol / 1_000).toFixed(1)}k`;
  return vol.toLocaleString('en-IN');
}

export function WatchlistManager() {
  const { data: watchlists, isLoading: isLoadingWatchlists } = useWatchlists(DEMO_USER_ID);
  const [activeWatchlistId, setActiveWatchlistId] = useState<string | null>(null);

  // Auto-select first watchlist if none selected
  const activeWatchlist = watchlists?.find((w) => w.id === activeWatchlistId) ?? watchlists?.[0];
  const currentId = activeWatchlist?.id ?? '';
  const { data: stocks, isLoading: isLoadingStocks } = useWatchlistStocks(currentId);

  // New watchlist modal / form state
  const [isCreatingList, setIsCreatingList] = useState(false);
  const [newListName, setNewListName] = useState('');
  const [newListDesc, setNewListDesc] = useState('');

  const createListMutation = useCreateWatchlist();
  const deleteListMutation = useDeleteWatchlist();
  const addStockMutation = useAddStock();
  const removeStockMutation = useRemoveStock();

  const handleCreateWatchlist = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newListName.trim()) return;
    createListMutation.mutate(
      { userId: DEMO_USER_ID, name: newListName.trim(), description: newListDesc.trim() },
      {
        onSuccess: (data: any) => {
          setNewListName('');
          setNewListDesc('');
          setIsCreatingList(false);
          if (data?.id) setActiveWatchlistId(data.id);
        },
      }
    );
  };

  const handleDeleteWatchlist = (id: string) => {
    if (watchlists && watchlists.length <= 1) {
      alert('You must keep at least one watchlist.');
      return;
    }
    if (!confirm('Are you sure you want to delete this watchlist and its stocks?')) return;
    deleteListMutation.mutate(
      { watchlistId: id, userId: DEMO_USER_ID },
      {
        onSuccess: () => {
          const remaining = watchlists?.filter((w) => w.id !== id);
          if (remaining && remaining.length > 0) {
            setActiveWatchlistId(remaining[0].id);
          }
        },
      }
    );
  };

  const handleAddStock = (symbol: string, companyName: string) => {
    if (!currentId) return;
    addStockMutation.mutate({
      watchlistId: currentId,
      symbol: symbol.toUpperCase(),
      companyName,
      userId: DEMO_USER_ID,
    });
  };

  const handleRemoveStock = (symbol: string) => {
    if (!currentId) return;
    removeStockMutation.mutate({
      watchlistId: currentId,
      symbol,
      userId: DEMO_USER_ID,
    });
  };

  return (
    <div className="space-y-6">
      {/* Watchlist Tabs / Selector */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] pb-4">
        <div className="flex flex-wrap items-center gap-2">
          {isLoadingWatchlists ? (
            <div className="h-9 w-32 bg-white/[0.06] rounded-lg animate-pulse"></div>
          ) : (
            watchlists?.map((wl) => {
              const isActive = wl.id === currentId;
              return (
                <button
                  key={wl.id}
                  onClick={() => setActiveWatchlistId(wl.id)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2 ${
                    isActive
                      ? 'bg-[#00d09c] text-slate-950 font-semibold shadow-md shadow-[#00d09c]/20'
                      : 'bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08]'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>{wl.name}</span>
                  {wl.item_count != null && (
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-bold transition-all ${
                        isActive ? 'bg-black/20 text-slate-950' : 'bg-white/[0.08] text-slate-300'
                      }`}
                    >
                      {wl.item_count}
                    </span>
                  )}
                </button>
              );
            })
          )}

          <button
            onClick={() => setIsCreatingList(true)}
            className="px-3.5 py-2 rounded-xl text-sm font-medium border border-dashed border-white/[0.15] text-slate-400 hover:text-white hover:border-[#00d09c] hover:bg-[#00d09c]/5 transition-all flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4 text-[#00d09c]" />
            <span>New Watchlist</span>
          </button>
        </div>

        {activeWatchlist && (
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleDeleteWatchlist(activeWatchlist.id)}
              disabled={deleteListMutation.isPending}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 transition-all flex items-center gap-1.5"
              title="Delete this watchlist"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete List</span>
            </button>
          </div>
        )}
      </div>

      {/* Create Watchlist Modal / Form */}
      {isCreatingList && (
        <form
          onSubmit={handleCreateWatchlist}
          className="p-5 bg-[#141720] rounded-2xl border border-white/[0.08] space-y-3.5 animate-in fade-in"
        >
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Create New Watchlist</h3>
            <button
              type="button"
              onClick={() => setIsCreatingList(false)}
              className="text-xs text-slate-400 hover:text-white"
            >
              Cancel
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <input
              type="text"
              placeholder="e.g. Energy & Defense"
              value={newListName}
              onChange={(e) => setNewListName(e.target.value)}
              className="px-3.5 py-2 bg-black/40 border border-white/[0.1] rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-[#00d09c]"
              required
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={newListDesc}
              onChange={(e) => setNewListDesc(e.target.value)}
              className="px-3.5 py-2 bg-black/40 border border-white/[0.1] rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-[#00d09c]"
            />
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={createListMutation.isPending}
              className="px-4 py-2 bg-[#00d09c] text-slate-950 font-semibold rounded-xl text-xs hover:bg-[#00b084] transition-all disabled:opacity-50"
            >
              {createListMutation.isPending ? 'Creating...' : 'Create Watchlist'}
            </button>
          </div>
        </form>
      )}

      {/* Quick Add Suggestions Bar */}
      <div className="bg-[#12141c] border border-white/[0.06] rounded-2xl p-4 sm:p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-[#00d09c]" />
            <span>Quick Add Popular Indian Stocks</span>
          </div>
          <span className="text-[11px] text-slate-500">Live prices attached automatically</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {POPULAR_SUGGESTIONS.map((stock) => {
            const isAlreadyAdded = stocks?.some((s) => s.symbol === stock.symbol);
            return (
              <button
                key={stock.symbol}
                type="button"
                disabled={isAlreadyAdded || addStockMutation.isPending}
                onClick={() => handleAddStock(stock.symbol, stock.name)}
                className={`text-xs px-3 py-1.5 rounded-xl border flex items-center gap-1.5 transition-all ${
                  isAlreadyAdded
                    ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400 opacity-60 cursor-default'
                    : 'bg-white/[0.03] border-white/[0.08] text-slate-300 hover:text-white hover:bg-white/[0.08] hover:border-white/[0.2] active:scale-95'
                }`}
              >
                {isAlreadyAdded ? (
                  <Check className="w-3.5 h-3.5" />
                ) : (
                  <Plus className="w-3.5 h-3.5 text-[#00d09c]" />
                )}
                <span className="font-semibold font-mono">{stock.symbol.replace('.NS', '')}</span>
                <span className="text-[10px] text-slate-400 hidden sm:inline">({stock.sector})</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Stocks in Active Watchlist */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white tracking-tight">
              Watched Stocks
            </h3>
            <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#00d09c]/15 text-[#00d09c] border border-[#00d09c]/20">
              {stocks?.length ?? 0}
            </span>
          </div>
          <p className="text-xs text-slate-500">
            Real-time quotes update with each CRUD action
          </p>
        </div>

        {isLoadingStocks ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 bg-white/[0.03] border border-white/[0.06] rounded-xl animate-pulse" />
            ))}
          </div>
        ) : stocks && stocks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {stocks.map((stock) => {
              const isPositive = (stock.daily_change ?? 0) >= 0;
              return (
                <div
                  key={stock.id}
                  className="bg-[#141720]/90 border border-white/[0.06] hover:border-white/[0.14] rounded-xl p-4 flex items-center justify-between gap-3 transition-all hover:shadow-lg hover:shadow-black/40 group"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold font-mono text-white tracking-wide">
                        {stock.symbol.replace('.NS', '')}
                      </span>
                      <span className="text-[11px] font-medium text-slate-500 border border-white/[0.06] px-1.5 py-0.5 rounded">
                        NSE
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 truncate mt-0.5">
                      {stock.company_name}
                    </div>
                    {stock.volume != null && (
                      <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-1.5">
                        <span>Vol:</span>
                        <span className="font-mono text-slate-400 font-medium">{formatVolume(stock.volume)}</span>
                      </div>
                    )}
                  </div>

                  {/* Price & Change Numbers */}
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-base font-bold font-mono text-white">
                        {stock.price != null
                          ? `₹${stock.price.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
                          : '—'}
                      </div>
                      <div
                        className={`text-xs font-semibold font-mono flex items-center justify-end gap-0.5 mt-0.5 ${
                          isPositive ? 'text-emerald-400' : 'text-rose-400'
                        }`}
                      >
                        {isPositive ? (
                          <TrendingUp className="w-3 h-3" />
                        ) : (
                          <TrendingDown className="w-3 h-3" />
                        )}
                        <span>
                          {stock.daily_change != null
                            ? `${isPositive ? '+' : ''}${stock.daily_change.toFixed(2)}%`
                            : '0.00%'}
                        </span>
                        {stock.daily_change_abs != null && (
                          <span className="text-[10px] text-slate-500 ml-1">
                            ({isPositive ? '+' : ''}₹{Math.abs(stock.daily_change_abs).toFixed(2)})
                          </span>
                        )}
                      </div>
                    </div>

                    <button
                      onClick={() => handleRemoveStock(stock.symbol)}
                      disabled={removeStockMutation.isPending}
                      className="p-2 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors opacity-60 group-hover:opacity-100"
                      title="Remove from watchlist"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-12 bg-white/[0.02] border border-dashed border-white/[0.08] rounded-2xl">
            <p className="text-sm text-slate-400">No stocks in this watchlist yet.</p>
            <p className="text-xs text-slate-500 mt-1">Use the quick add chips above to add your first stock!</p>
          </div>
        )}
      </div>
    </div>
  );
}
