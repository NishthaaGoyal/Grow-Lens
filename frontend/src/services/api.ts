/**
 * Groww Lens — API client (axios-free, uses native fetch + TanStack Query pattern)
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1';

// Default demo user ID (no auth for MVP)
export const DEMO_USER_ID = 'a0000000-0000-0000-0000-000000000001';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

// ─────────────────────────────────────────────
// Users
// ─────────────────────────────────────────────
export const usersApi = {
  getDemoUser: () => request('/users/demo/user'),
  getUser: (id: string) => request(`/users/${id}`),
  create: (name: string, email: string) =>
    request('/users/', { method: 'POST', body: JSON.stringify({ name, email }) }),
};

// ─────────────────────────────────────────────
// Watchlists
// ─────────────────────────────────────────────
export const watchlistsApi = {
  list: (userId: string) => request(`/watchlists/?user_id=${userId}`),
  create: (userId: string, name: string, description?: string) =>
    request(`/watchlists/?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    }),
  delete: (id: string) => request(`/watchlists/${id}`, { method: 'DELETE' }),
  listStocks: (watchlistId: string) => request(`/watchlists/${watchlistId}/stocks`),
  addStock: (watchlistId: string, symbol: string, company_name: string) =>
    request(`/watchlists/${watchlistId}/stocks`, {
      method: 'POST',
      body: JSON.stringify({ symbol, company_name }),
    }),
  removeStock: (watchlistId: string, symbol: string) =>
    request(`/watchlists/${watchlistId}/stocks/${symbol}`, { method: 'DELETE' }),
};

// ─────────────────────────────────────────────
// Snapshots
// ─────────────────────────────────────────────
export const snapshotsApi = {
  create: (userId: string, triggerType = 'manual') =>
    request('/snapshots/create', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, trigger_type: triggerType }),
    }),
  getLatest: (userId: string) => request(`/snapshots/latest?user_id=${userId}`),
  list: (userId: string, limit = 10) =>
    request(`/snapshots/?user_id=${userId}&limit=${limit}`),
};

// ─────────────────────────────────────────────
// Events
// ─────────────────────────────────────────────
export const eventsApi = {
  list: (userId: string, options?: { unreadOnly?: boolean; limit?: number }) =>
    request(
      `/events/?user_id=${userId}&unread_only=${options?.unreadOnly ?? false}&limit=${options?.limit ?? 50}`
    ),
  highImpact: (userId: string, threshold = 60) =>
    request(`/events/high-impact?user_id=${userId}&threshold=${threshold}`),
  markRead: (eventIds: string[]) =>
    request('/events/mark-read', {
      method: 'POST',
      body: JSON.stringify({ event_ids: eventIds }),
    }),
  get: (eventId: string) => request(`/events/${eventId}`),
};

// ─────────────────────────────────────────────
// Dashboard
// ─────────────────────────────────────────────
export const dashboardApi = {
  whileAway: (userId: string) => request(`/dashboard/while-away?user_id=${userId}`),
  pulse: () => request('/dashboard/pulse'),
};
