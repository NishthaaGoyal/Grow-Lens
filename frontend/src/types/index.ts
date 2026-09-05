/**
 * Groww Lens — TypeScript type definitions for API data models.
 */

// ─────────────────────────────────────────────
// User
// ─────────────────────────────────────────────
export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

// ─────────────────────────────────────────────
// Watchlist
// ─────────────────────────────────────────────
export interface Watchlist {
  id: string;
  user_id: string;
  name: string;
  description?: string | null;
  created_at: string;
  item_count?: number;
}

export interface WatchlistItem {
  id: string;
  watchlist_id: string;
  symbol: string;
  company_name: string;
  added_at: string;
  price?: number;
  daily_change?: number;
  daily_change_abs?: number;
  volume?: number;
  avg_volume?: number;
}

// ─────────────────────────────────────────────
// Snapshot
// ─────────────────────────────────────────────
export interface SnapshotItem {
  id: string;
  snapshot_id: string;
  symbol: string;
  company_name: string;
  price: number;
  daily_change: number;
  volume: number;
  created_at: string;
}

export interface Snapshot {
  id: string;
  user_id: string;
  snapshot_time: string;
  trigger_type: string;
  items: SnapshotItem[];
}

// ─────────────────────────────────────────────
// Events
// ─────────────────────────────────────────────
export type EventType =
  | 'price_surge'
  | 'price_drop'
  | 'volume_spike'
  | 'news_event'
  | 'volatility_increase'
  | 'sector_movement'
  | 'all_time_high'
  | 'all_time_low'
  | 'minor_fluctuation';

export interface MarketEvent {
  id: string;
  user_id: string;
  symbol: string;
  company_name?: string | null;
  event_type: EventType;
  impact_score: number; // 0–100
  summary: string;
  explanation?: string | null;
  price_change?: number | null;
  volume_ratio?: number | null;
  metadata?: Record<string, unknown>;
  is_read: boolean;
  created_at: string;
}

// ─────────────────────────────────────────────
// Market Pulse
// ─────────────────────────────────────────────
export type MarketMood = 'Bullish' | 'Bearish' | 'Neutral' | 'Volatile';

export interface MarketPulse {
  id: string;
  pulse_date: string; // YYYY-MM-DD
  market_mood?: MarketMood | null;
  strongest_sector?: string | null;
  weakest_sector?: string | null;
  top_theme?: string | null;
  global_sentiment?: string | null;
  summary?: string | null;
  ai_narrative?: string | null;
}

// ─────────────────────────────────────────────
// Dashboard — While You Were Away
// ─────────────────────────────────────────────
export interface WhileAwayStats {
  hours_away: number;
  total_events: number;
  high_impact_events: number;
  medium_impact_events: number;
  low_impact_events: number;
  last_snapshot_time?: string | null;
}

export interface WhileAwayResponse {
  user_id: string;
  stats: WhileAwayStats;
  events: MarketEvent[];
  pulse?: MarketPulse | null;
}

// ─────────────────────────────────────────────
// UI helpers
// ─────────────────────────────────────────────
export interface EventCardProps {
  event: MarketEvent;
  expanded?: boolean;
  onToggle?: () => void;
}

export interface ImpactBadgeProps {
  score: number;
}

export type ImpactLevel = 'high' | 'medium' | 'low';

export function getImpactLevel(score: number): ImpactLevel {
  if (score >= 60) return 'high';
  if (score >= 30) return 'medium';
  return 'low';
}

export function getEventEmoji(eventType: EventType): string {
  const map: Record<EventType, string> = {
    price_surge: '🚀',
    price_drop: '📉',
    volume_spike: '📊',
    news_event: '📰',
    volatility_increase: '⚡',
    sector_movement: '🌍',
    all_time_high: '🏆',
    all_time_low: '🔻',
    minor_fluctuation: '〰️',
  };
  return map[eventType] ?? '📌';
}

export function getImpactEmoji(score: number): string {
  if (score >= 75) return '🚨';
  if (score >= 45) return '⚠️';
  return '💤';
}

export function formatPriceChange(change: number | null | undefined): string {
  if (change == null) return '—';
  const sign = change > 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}%`;
}

export function formatVolumeRatio(ratio: number | null | undefined): string {
  if (ratio == null) return '—';
  return `${ratio.toFixed(1)}× avg`;
}
