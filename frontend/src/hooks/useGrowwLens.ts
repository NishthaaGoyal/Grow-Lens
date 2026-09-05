/**
 * TanStack Query hooks for all Groww Lens API endpoints.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  dashboardApi, watchlistsApi, snapshotsApi, eventsApi,
  DEMO_USER_ID,
} from '@/services/api';
import type {
  WhileAwayResponse, MarketPulse, Watchlist, WatchlistItem,
  MarketEvent, Snapshot,
} from '@/types';

// ─── Query Keys ───────────────────────────────────────────────────────────────
export const QueryKeys = {
  whileAway: (userId: string) => ['dashboard', 'while-away', userId],
  pulse: () => ['dashboard', 'pulse'],
  watchlists: (userId: string) => ['watchlists', userId],
  watchlistStocks: (watchlistId: string) => ['watchlists', watchlistId, 'stocks'],
  events: (userId: string) => ['events', userId],
  highImpactEvents: (userId: string) => ['events', 'high-impact', userId],
  latestSnapshot: (userId: string) => ['snapshots', 'latest', userId],
};

// ─── Dashboard ────────────────────────────────────────────────────────────────
export function useWhileAway(userId = DEMO_USER_ID) {
  return useQuery<WhileAwayResponse>({
    queryKey: QueryKeys.whileAway(userId),
    queryFn: () => dashboardApi.whileAway(userId) as Promise<WhileAwayResponse>,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: 1,
  });
}

export function useMarketPulse() {
  return useQuery<MarketPulse>({
    queryKey: QueryKeys.pulse(),
    queryFn: () => dashboardApi.pulse() as Promise<MarketPulse>,
    staleTime: 30 * 60 * 1000, // 30 minutes
    retry: 1,
  });
}

// ─── Watchlists ───────────────────────────────────────────────────────────────
export function useWatchlists(userId = DEMO_USER_ID) {
  return useQuery<Watchlist[]>({
    queryKey: QueryKeys.watchlists(userId),
    queryFn: () => watchlistsApi.list(userId) as Promise<Watchlist[]>,
    staleTime: 5 * 60 * 1000,
  });
}

export function useWatchlistStocks(watchlistId: string) {
  return useQuery<WatchlistItem[]>({
    queryKey: QueryKeys.watchlistStocks(watchlistId),
    queryFn: () => watchlistsApi.listStocks(watchlistId) as Promise<WatchlistItem[]>,
    enabled: !!watchlistId,
  });
}

export function useCreateWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, name, description }: { userId: string; name: string; description?: string }) =>
      watchlistsApi.create(userId, name, description),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.watchlists(userId) });
      queryClient.invalidateQueries({ queryKey: QueryKeys.whileAway(userId) });
    },
  });
}

export function useDeleteWatchlist() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ watchlistId }: { watchlistId: string; userId?: string }) =>
      watchlistsApi.delete(watchlistId),
    onSuccess: (_, { userId = DEMO_USER_ID }) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.watchlists(userId) });
      queryClient.invalidateQueries({ queryKey: QueryKeys.whileAway(userId) });
    },
  });
}

export function useAddStock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ watchlistId, symbol, companyName }: { watchlistId: string; symbol: string; companyName: string; userId?: string }) =>
      watchlistsApi.addStock(watchlistId, symbol, companyName),
    onSuccess: (_, { watchlistId, userId = DEMO_USER_ID }) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.watchlistStocks(watchlistId) });
      queryClient.invalidateQueries({ queryKey: QueryKeys.watchlists(userId) });
      queryClient.invalidateQueries({ queryKey: QueryKeys.whileAway(userId) });
    },
  });
}

export function useRemoveStock() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ watchlistId, symbol }: { watchlistId: string; symbol: string; userId?: string }) =>
      watchlistsApi.removeStock(watchlistId, symbol),
    onSuccess: (_, { watchlistId, userId = DEMO_USER_ID }) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.watchlistStocks(watchlistId) });
      queryClient.invalidateQueries({ queryKey: QueryKeys.watchlists(userId) });
      queryClient.invalidateQueries({ queryKey: QueryKeys.whileAway(userId) });
    },
  });
}

// ─── Snapshots ────────────────────────────────────────────────────────────────
export function useLatestSnapshot(userId = DEMO_USER_ID) {
  return useQuery<Snapshot>({
    queryKey: QueryKeys.latestSnapshot(userId),
    queryFn: () => snapshotsApi.getLatest(userId) as Promise<Snapshot>,
  });
}

export function useCreateSnapshot() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, triggerType }: { userId: string; triggerType?: string }) =>
      snapshotsApi.create(userId, triggerType),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.latestSnapshot(userId) });
    },
  });
}

// ─── Events ───────────────────────────────────────────────────────────────────
export function useEvents(userId = DEMO_USER_ID, unreadOnly = false) {
  return useQuery<MarketEvent[]>({
    queryKey: [...QueryKeys.events(userId), { unreadOnly }],
    queryFn: () => eventsApi.list(userId, { unreadOnly }) as Promise<MarketEvent[]>,
    staleTime: 2 * 60 * 1000,
  });
}

export function useHighImpactEvents(userId = DEMO_USER_ID) {
  return useQuery<MarketEvent[]>({
    queryKey: QueryKeys.highImpactEvents(userId),
    queryFn: () => eventsApi.highImpact(userId) as Promise<MarketEvent[]>,
    staleTime: 2 * 60 * 1000,
  });
}

export function useMarkEventsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ eventIds, userId }: { eventIds: string[]; userId: string }) =>
      eventsApi.markRead(eventIds),
    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: QueryKeys.events(userId) });
      queryClient.invalidateQueries({ queryKey: QueryKeys.whileAway(userId) });
    },
  });
}
