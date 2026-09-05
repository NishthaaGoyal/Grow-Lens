# Groww Lens — Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│         Next.js 15 + TypeScript + TailwindCSS               │
│                                                             │
│  ┌──────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │  Dashboard   │  │   Watchlists   │  │  Event Detail  │  │
│  │ While Away   │  │  (Manage stocks│  │   + Explain    │  │
│  │ Market Pulse │  │   Create/Edit) │  │                │  │
│  └──────┬───────┘  └───────┬────────┘  └───────┬────────┘  │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘           │
│                       TanStack Query                         │
└─────────────────────────┬───────────────────────────────────┘
                           │ HTTP / REST
┌──────────────────────────▼──────────────────────────────────┐
│                       BACKEND                                │
│              FastAPI + Python 3.11                           │
│                                                             │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │  Watchlist │  │  Snapshot   │  │  Dashboard           │  │
│  │  API       │  │  API        │  │  /while-away, /pulse │  │
│  └────────────┘  └─────────────┘  └──────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               SERVICE LAYER                           │  │
│  │  MarketData │ ChangeDetection │ ImpactScorer │ AI     │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────┐    ┌──────────────────────────────┐   │
│  │   PostgreSQL     │    │          Redis               │   │
│  │  users           │    │  market:quote:{symbol}       │   │
│  │  watchlists      │    │  events:user:{id}            │   │
│  │  watchlist_items │    │  pulse:{date}                │   │
│  │  snapshots       │    └──────────────────────────────┘   │
│  │  snapshot_items  │                                       │
│  │  events          │    ┌──────────────────────────────┐   │
│  │  market_pulse    │    │    External APIs              │   │
│  └──────────────────┘    │  yfinance (market data)      │   │
│                           │  Gemini API (AI)             │   │
│                           │  NewsAPI / Finnhub (news)    │   │
│                           └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Core Data Flow — "While You Were Away"

```
User Returns
    │
    ▼
GET /dashboard/while-away?user_id={id}
    │
    ├─► Fetch latest Snapshot from DB
    │       (what user last saw)
    │
    ├─► Fetch current market data
    │       MarketDataService → yfinance
    │       (with Redis cache, TTL 60s)
    │
    ├─► Change Detection
    │       ChangeDetectionService
    │       Compares: snapshot_price vs current_price
    │                 snapshot_volume vs avg_volume
    │       Outputs: List[RawEvent]
    │
    ├─► Impact Scoring
    │       ImpactScorerService
    │       Formula: 30% price + 25% volume + 20% news
    │                + 15% volatility + 10% relevance
    │       Sorts: by impact_score DESC
    │
    ├─► AI Explanation (top 5 events)
    │       AIExplainerService → Gemini API
    │       Generates: "Why it matters" in plain English
    │
    ├─► Persist Events to DB
    │
    └─► Return WhileAwayResponse
            ├── stats (hours away, event counts)
            ├── events (sorted by impact)
            └── pulse (today's market pulse)
```

## Impact Score Formula

```
Impact Score = (
    0.30 × price_score      # Sigmoid: 0% → 0, 5% → 50, 10%+ → ~95
  + 0.25 × volume_score     # Linear: 1x → 0, 2x → 33, 4x+ → 100
  + 0.20 × news_score       # Event type proxy until Phase 5
  + 0.15 × volatility_score # Price × volume combined
  + 0.10 × relevance_score  # Watchlist membership boost
)
```

## Event Types

| Event Type | Trigger | Typical Score |
|---|---|---|
| `price_surge` | Price +2%+ since snapshot | 60–95 |
| `price_drop` | Price -2%+ since snapshot | 60–95 |
| `volume_spike` | Volume 1.5x+ avg, small price move | 30–60 |
| `news_event` | News detected (Phase 5) | 50–90 |
| `volatility_increase` | High price + high volume | 40–75 |
| `minor_fluctuation` | No threshold crossed | 5–30 |

## Snapshot Triggers

| Trigger | Description |
|---|---|
| `session_exit` | User closes the tab or navigates away |
| `logout` | User explicitly logs out |
| `session_expire` | Session timeout detected |
| `scheduled` | Hourly cron snapshot |
| `manual` | API call (dev/testing) |
