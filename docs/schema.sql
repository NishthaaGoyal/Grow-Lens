-- ==============================================================================
-- Groww Lens — PostgreSQL Database Schema & Seed (Supabase Compatible)
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

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

-- Trigger
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

-- Disable RLS for backend service access
ALTER TABLE public.users DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.watchlists DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.watchlist_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.snapshots DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.snapshot_items DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.events DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.market_pulse DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.news_cache DISABLE ROW LEVEL SECURITY;

-- Demo Seed
INSERT INTO public.users (id, name, email) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Demo User', 'demo@growwlens.in')
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.watchlists (id, user_id, name, description) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'Technology', 'Top Indian IT stocks'),
    ('b0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000001', 'Auto & EV', 'Automobile and EV sector stocks')
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.watchlist_items (watchlist_id, symbol, company_name) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'INFY.NS',        'Infosys Limited'),
    ('b0000000-0000-0000-0000-000000000001', 'TCS.NS',         'Tata Consultancy Services'),
    ('b0000000-0000-0000-0000-000000000001', 'WIPRO.NS',       'Wipro Limited'),
    ('b0000000-0000-0000-0000-000000000002', 'TATAMOTORS.NS',  'Tata Motors Limited'),
    ('b0000000-0000-0000-0000-000000000002', 'M&M.NS',         'Mahindra & Mahindra'),
    ('b0000000-0000-0000-0000-000000000002', 'OLECTRA.NS',     'Olectra Greentech')
ON CONFLICT (watchlist_id, symbol) DO NOTHING;
