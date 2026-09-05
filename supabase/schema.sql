-- ==============================================================================
-- Groww Lens — Supabase PostgreSQL Schema & Initial Seed
-- ==============================================================================
-- Copy and paste this script directly into the Supabase SQL Editor:
-- Dashboard -> Your Project -> SQL Editor -> New Query -> Run
-- ==============================================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==============================================================================
-- 2. CREATE TABLES
-- ==============================================================================

-- Table: users
CREATE TABLE IF NOT EXISTS public.users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table: watchlists
CREATE TABLE IF NOT EXISTS public.watchlists (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_watchlists_user_id ON public.watchlists(user_id);

-- Table: watchlist_items
CREATE TABLE IF NOT EXISTS public.watchlist_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    watchlist_id    UUID NOT NULL REFERENCES public.watchlists(id) ON DELETE CASCADE,
    symbol          VARCHAR(50) NOT NULL,
    company_name    VARCHAR(255) NOT NULL,
    added_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_watchlist_symbol UNIQUE(watchlist_id, symbol)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_items_watchlist_id ON public.watchlist_items(watchlist_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_items_symbol ON public.watchlist_items(symbol);

-- Table: snapshots
CREATE TABLE IF NOT EXISTS public.snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    snapshot_time   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    trigger_type    VARCHAR(50) NOT NULL DEFAULT 'manual',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_snapshots_user_id ON public.snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_snapshots_snapshot_time ON public.snapshots(snapshot_time DESC);

-- Table: snapshot_items
CREATE TABLE IF NOT EXISTS public.snapshot_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id     UUID NOT NULL REFERENCES public.snapshots(id) ON DELETE CASCADE,
    symbol          VARCHAR(50) NOT NULL,
    company_name    VARCHAR(255) NOT NULL,
    price           DECIMAL(18, 4) NOT NULL,
    daily_change    DECIMAL(8, 4) NOT NULL,
    daily_change_abs DECIMAL(18, 4),
    volume          BIGINT NOT NULL,
    avg_volume      BIGINT,
    market_cap      BIGINT,
    high_52w        DECIMAL(18, 4),
    low_52w         DECIMAL(18, 4),
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_snapshot_items_snapshot_id ON public.snapshot_items(snapshot_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_items_symbol ON public.snapshot_items(symbol);

-- Table: events
CREATE TABLE IF NOT EXISTS public.events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    symbol          VARCHAR(50) NOT NULL,
    company_name    VARCHAR(255),
    event_type      VARCHAR(100) NOT NULL,
    impact_score    INTEGER NOT NULL CHECK (impact_score >= 0 AND impact_score <= 100),
    summary         TEXT NOT NULL,
    explanation     TEXT,
    price_change    DECIMAL(8, 4),
    volume_ratio    DECIMAL(8, 2),
    metadata        JSONB DEFAULT '{}',
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_events_user_id ON public.events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_symbol ON public.events(symbol);
CREATE INDEX IF NOT EXISTS idx_events_impact_score ON public.events(impact_score DESC);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON public.events(created_at DESC);

-- Table: market_pulse
CREATE TABLE IF NOT EXISTS public.market_pulse (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pulse_date      DATE NOT NULL UNIQUE,
    market_mood     VARCHAR(50),
    strongest_sector VARCHAR(100),
    weakest_sector  VARCHAR(100),
    top_theme       VARCHAR(255),
    global_sentiment VARCHAR(50),
    summary         TEXT,
    ai_narrative    TEXT,
    raw_data        JSONB DEFAULT '{}',
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_market_pulse_date ON public.market_pulse(pulse_date DESC);

-- Table: news_cache
CREATE TABLE IF NOT EXISTS public.news_cache (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol          VARCHAR(50),
    headline        TEXT NOT NULL,
    source          VARCHAR(255),
    url             TEXT,
    published_at    TIMESTAMP WITH TIME ZONE,
    sentiment       VARCHAR(20),
    sentiment_score DECIMAL(5, 4),
    fetched_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_cache_symbol ON public.news_cache(symbol);
CREATE INDEX IF NOT EXISTS idx_news_cache_published_at ON public.news_cache(published_at DESC);

-- ==============================================================================
-- 3. UPDATED_AT TRIGGER FUNCTION
-- ==============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_watchlists_updated_at ON public.watchlists;
CREATE TRIGGER update_watchlists_updated_at
    BEFORE UPDATE ON public.watchlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================================================
-- 4. DISABLE RLS (Ensure Direct / Backend API Access Works Without Blockers)
-- ==============================================================================
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.watchlists DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.watchlist_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.snapshots DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.snapshot_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.events DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_pulse DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.news_cache DISABLE ROW LEVEL SECURITY;

-- ==============================================================================
-- 5. INITIAL SEED DATA (Demo User, Watchlists, Stocks, Snapshot, Events & Pulse)
-- ==============================================================================

-- 5.1 Demo User
INSERT INTO public.users (id, name, email) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Demo User', 'demo@growwlens.in')
ON CONFLICT (id) DO NOTHING;

-- 5.2 Watchlists
INSERT INTO public.watchlists (id, user_id, name, description) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Technology', 'Top Indian IT stocks'),
    ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'Auto & EV', 'Automobile and EV sector stocks')
ON CONFLICT (id) DO NOTHING;

-- 5.3 Watchlist Items
INSERT INTO public.watchlist_items (watchlist_id, symbol, company_name) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'INFY.NS',        'Infosys Limited'),
    ('b0000000-0000-0000-0000-000000000001', 'TCS.NS',         'Tata Consultancy Services'),
    ('b0000000-0000-0000-0000-000000000001', 'WIPRO.NS',       'Wipro Limited'),
    ('b0000000-0000-0000-0000-000000000002', 'TATAMOTORS.NS',  'Tata Motors Limited'),
    ('b0000000-0000-0000-0000-000000000002', 'M&M.NS',         'Mahindra & Mahindra'),
    ('b0000000-0000-0000-0000-000000000002', 'OLECTRA.NS',     'Olectra Greentech')
ON CONFLICT (watchlist_id, symbol) DO NOTHING;

-- 5.4 Baseline Snapshot (Simulating user state 12 hours ago)
INSERT INTO public.snapshots (id, user_id, snapshot_time, trigger_type) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', NOW() - INTERVAL '12 hours', 'session_exit')
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.snapshot_items (snapshot_id, symbol, company_name, price, daily_change, volume, avg_volume) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'INFY.NS',        'Infosys Limited',          1820.00,  0.45, 1850000, 2000000),
    ('c0000000-0000-0000-0000-000000000001', 'TCS.NS',         'Tata Consultancy Services', 4080.00, -0.20, 1200000, 1400000),
    ('c0000000-0000-0000-0000-000000000001', 'WIPRO.NS',       'Wipro Limited',             475.00,  0.10,  950000, 1100000),
    ('c0000000-0000-0000-0000-000000000001', 'TATAMOTORS.NS',  'Tata Motors Limited',       830.00,  1.10, 3200000, 2800000),
    ('c0000000-0000-0000-0000-000000000001', 'M&M.NS',         'Mahindra & Mahindra',      3050.00,  0.80, 1400000, 1500000),
    ('c0000000-0000-0000-0000-000000000001', 'OLECTRA.NS',     'Olectra Greentech',        1390.00,  1.50,  850000,  800000)
ON CONFLICT DO NOTHING;

-- 5.5 Market Events (Ranked by Impact Score with AI Explanations)
INSERT INTO public.events (id, user_id, symbol, company_name, event_type, impact_score, summary, explanation, price_change, volume_ratio, metadata, is_read) VALUES
(
    'd0000000-0000-0000-0000-000000000001',
    'a0000000-0000-0000-0000-000000000001',
    'OLECTRA.NS',
    'Olectra Greentech',
    'price_surge',
    94,
    'Olectra Greentech gained 6.5% since your last visit (₹1390 → ₹1480). ₹500Cr government order secured',
    'Olectra has surged 6.5% on very high trading volume (4.2x average), driven by a major government electric bus order worth ₹500 crore. This kind of institutional order significantly boosts multi-quarter revenue visibility.',
    6.50,
    4.20,
    '{"snapshot_price": 1390.0, "current_price": 1480.35, "volume_ratio": 4.2}',
    FALSE
),
(
    'd0000000-0000-0000-0000-000000000002',
    'a0000000-0000-0000-0000-000000000001',
    'TATAMOTORS.NS',
    'Tata Motors Limited',
    'price_surge',
    91,
    'Tata Motors Limited gained 4.8% since your last visit (₹830 → ₹870). Quarterly sales announcement released with record EV numbers',
    'Tata Motors gained 4.8% with nearly 3x normal trading activity, backed by a strong quarterly sales announcement with record EV deliveries. High volume alongside positive commercial delivery news signals genuine institutional conviction.',
    4.80,
    2.90,
    '{"snapshot_price": 830.0, "current_price": 869.84, "volume_ratio": 2.9}',
    FALSE
),
(
    'd0000000-0000-0000-0000-000000000003',
    'a0000000-0000-0000-0000-000000000001',
    'M&M.NS',
    'Mahindra & Mahindra',
    'price_surge',
    79,
    'Mahindra & Mahindra gained 3.2% since your last visit (₹3050 → ₹3148). New EV model launch event announced',
    'Mahindra & Mahindra rose 3.2% ahead of a new electric vehicle model launch event. EV-related announcements have been drawing notable buying momentum across automotive peers.',
    3.20,
    2.10,
    '{"snapshot_price": 3050.0, "current_price": 3147.60, "volume_ratio": 2.1}',
    FALSE
),
(
    'd0000000-0000-0000-0000-000000000004',
    'a0000000-0000-0000-0000-000000000001',
    'INFY.NS',
    'Infosys Limited',
    'price_surge',
    76,
    'Infosys Limited gained 2.3% since your last visit (₹1820 → ₹1862). Large enterprise client deal announced',
    'Infosys gained 2.3% following the announcement of a large enterprise client contract. Such multi-year deals improve future billing visibility and sustain investor confidence.',
    2.30,
    1.80,
    '{"snapshot_price": 1820.0, "current_price": 1861.86, "volume_ratio": 1.8}',
    FALSE
),
(
    'd0000000-0000-0000-0000-000000000005',
    'a0000000-0000-0000-0000-000000000001',
    'WIPRO.NS',
    'Wipro Limited',
    'minor_fluctuation',
    22,
    'Wipro Limited gained 1.1% since your last visit (₹475 → ₹480)',
    'Wipro saw a routine 1.1% uptick on normal trading volume with no specific company-specific catalyst — moves are aligned with general IT index momentum.',
    1.10,
    1.20,
    '{"snapshot_price": 475.0, "current_price": 480.22, "volume_ratio": 1.2}',
    FALSE
),
(
    'd0000000-0000-0000-0000-000000000006',
    'a0000000-0000-0000-0000-000000000001',
    'TCS.NS',
    'Tata Consultancy Services',
    'minor_fluctuation',
    12,
    'Tata Consultancy Services dropped 0.9% since your last visit (₹4080 → ₹4043)',
    'TCS recorded a minor 0.9% drift on below-average volume. Normal market noise without negative structural events.',
    -0.90,
    0.90,
    '{"snapshot_price": 4080.0, "current_price": 4043.28, "volume_ratio": 0.9}',
    FALSE
)
ON CONFLICT (id) DO NOTHING;

-- 5.6 Daily Market Pulse
INSERT INTO public.market_pulse (
    id,
    pulse_date,
    market_mood,
    strongest_sector,
    weakest_sector,
    top_theme,
    global_sentiment,
    summary,
    ai_narrative,
    raw_data
) VALUES (
    'e0000000-0000-0000-0000-000000000001',
    CURRENT_DATE,
    'Bullish',
    'Auto & EV',
    'Pharma',
    'EV Orders & Green Mobility',
    'Positive',
    'Auto and EV sectors are leading today''s rally as government tender wins and strong delivery volume bolster sentiment.',
    'Indian equity markets opened higher today led by decisive strength in automotive and clean mobility counters. Heavy institutional volume was observed in mid-cap EV suppliers following state bus contract awards. IT stocks traded mildly positive following mid-tier deal announcements.',
    '{"sectors": {"Auto & EV": 3.1, "Technology": 0.8, "Banking": 0.4, "Pharma": -0.6, "Energy": 0.9}}'::jsonb
)
ON CONFLICT (pulse_date) DO UPDATE SET
    market_mood = EXCLUDED.market_mood,
    strongest_sector = EXCLUDED.strongest_sector,
    weakest_sector = EXCLUDED.weakest_sector,
    top_theme = EXCLUDED.top_theme,
    global_sentiment = EXCLUDED.global_sentiment,
    summary = EXCLUDED.summary,
    ai_narrative = EXCLUDED.ai_narrative,
    raw_data = EXCLUDED.raw_data;
