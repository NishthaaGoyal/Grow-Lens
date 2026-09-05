"""
Dashboard endpoints — the core "While You Were Away" and Market Pulse views.
Features auto-generation of baseline snapshots and real-time market pulse generation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone, date
from typing import Optional

from app.database.session import get_db
from app.models.models import Snapshot, SnapshotItem, Event, MarketPulse, Watchlist, WatchlistItem, User
from app.schemas.schemas import WhileAwayResponse, WhileAwayStats, MarketPulseOut, EventOut
from app.services.change_detection import ChangeDetectionService
from app.services.market_data import MarketDataService
from app.services.impact_scorer import ImpactScorerService
from app.services.ai_explainer import AIExplainerService, MarketPulseGenerator
from app.utils.cache import cache, pulse_key
from app.core.config import settings

router = APIRouter()

DEFAULT_DEMO_USER_ID = UUID("a0000000-0000-0000-0000-000000000001")


@router.get("/while-away", response_model=WhileAwayResponse)
async def while_you_were_away(
    user_id: Optional[UUID] = Query(DEFAULT_DEMO_USER_ID, description="Target user ID (defaults to demo user)"),
    db: AsyncSession = Depends(get_db),
):
    """
    The signature "While You Were Away" intelligence feed.
    Compares current market quotes with the user's previous snapshot,
    detects material price/volume events, scores them by impact (0-100),
    and attaches plain-English AI explanations.
    """
    target_user_id = user_id or DEFAULT_DEMO_USER_ID

    # 1. Ensure user exists
    user_result = await db.execute(select(User).where(User.id == target_user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        # Create demo user on the fly if needed
        user = User(id=target_user_id, name="Demo User", email="demo@growwlens.in")
        db.add(user)
        await db.flush()

    # 2. Get latest snapshot
    snap_result = await db.execute(
        select(Snapshot)
        .where(Snapshot.user_id == target_user_id)
        .order_by(Snapshot.snapshot_time.desc())
        .limit(1)
    )
    latest_snapshot = snap_result.scalar_one_or_none()

    # If no snapshot exists yet, check if user has watchlists to create one
    if not latest_snapshot:
        items_in_watchlist = await db.execute(
            select(WatchlistItem)
            .join(Watchlist, WatchlistItem.watchlist_id == Watchlist.id)
            .where(Watchlist.user_id == target_user_id)
        )
        stocks = items_in_watchlist.scalars().all()

        if not stocks:
            # Seed default demo watchlist for immediate evaluation
            tech_list = Watchlist(user_id=target_user_id, name="Technology", description="Top IT stocks")
            auto_list = Watchlist(user_id=target_user_id, name="Auto & EV", description="Leading auto & EV stocks")
            db.add_all([tech_list, auto_list])
            await db.flush()

            default_items = [
                WatchlistItem(watchlist_id=tech_list.id, symbol="INFY.NS", company_name="Infosys Limited"),
                WatchlistItem(watchlist_id=tech_list.id, symbol="TCS.NS", company_name="Tata Consultancy Services"),
                WatchlistItem(watchlist_id=auto_list.id, symbol="TATAMOTORS.NS", company_name="Tata Motors Limited"),
                WatchlistItem(watchlist_id=auto_list.id, symbol="M&M.NS", company_name="Mahindra & Mahindra"),
            ]
            db.add_all(default_items)
            await db.flush()
            stocks = default_items

        # Create initial baseline snapshot
        market_svc = MarketDataService()
        symbols = [s.symbol for s in stocks]
        quotes = await market_svc.get_quotes(symbols)

        # Baseline timestamp 8 hours ago to simulate time away
        baseline_time = datetime.now(timezone.utc) - timedelta(hours=8)
        latest_snapshot = Snapshot(
            user_id=target_user_id,
            snapshot_time=baseline_time,
            trigger_type="session_exit",
        )
        db.add(latest_snapshot)
        await db.flush()

        for s in stocks:
            q = quotes.get(s.symbol, {})
            price = q.get("price", 1000.0)
            # Give baseline slightly earlier price to demonstrate change
            item = SnapshotItem(
                snapshot_id=latest_snapshot.id,
                symbol=s.symbol,
                company_name=s.company_name,
                price=round(price * 0.965, 2),  # Simulated prior price
                daily_change=q.get("daily_change", 0.0),
                volume=q.get("volume", 1500000),
                avg_volume=q.get("avg_volume", 1500000),
            )
            db.add(item)
        await db.flush()

    # 3. Load snapshot items
    items_result = await db.execute(
        select(SnapshotItem).where(SnapshotItem.snapshot_id == latest_snapshot.id)
    )
    snapshot_items = items_result.scalars().all()

    # 4. Calculate time away
    snap_time = latest_snapshot.snapshot_time
    if snap_time and snap_time.tzinfo is None:
        snap_time = snap_time.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    hours_away = max(0.1, (now - snap_time).total_seconds() / 3600) if snap_time else 1.0

    # 5. Fetch current market data
    symbols = [item.symbol for item in snapshot_items]
    market_svc = MarketDataService()
    current_quotes = await market_svc.get_quotes(symbols)

    # 6. Detect changes
    detection_svc = ChangeDetectionService()
    raw_events = detection_svc.detect(snapshot_items, current_quotes)

    # 7. Score and sort by impact score DESC
    scorer = ImpactScorerService()
    scored_events = [scorer.score(ev) for ev in raw_events]
    scored_events.sort(key=lambda e: e["impact_score"], reverse=True)

    # 8. Generate AI explanations for top events
    explainer = AIExplainerService()
    for ev in scored_events[:5]:
        if not ev.get("explanation"):
            ev["explanation"] = await explainer.explain(ev)

    # 9. Persist events to DB
    db_events = []
    for ev in scored_events:
        event_obj = Event(
            user_id=target_user_id,
            symbol=ev["symbol"],
            company_name=ev.get("company_name"),
            event_type=ev["event_type"],
            impact_score=ev["impact_score"],
            summary=ev["summary"],
            explanation=ev.get("explanation"),
            price_change=ev.get("price_change"),
            volume_ratio=ev.get("volume_ratio"),
            event_metadata=ev.get("metadata", {}),
        )
        db.add(event_obj)
        db_events.append(event_obj)
    await db.flush()

    # 10. Categorize counts
    high = sum(1 for e in scored_events if e["impact_score"] >= settings.HIGH_IMPACT_THRESHOLD)
    medium = sum(1 for e in scored_events if 30 <= e["impact_score"] < settings.HIGH_IMPACT_THRESHOLD)
    low = sum(1 for e in scored_events if e["impact_score"] < 30)

    # 11. Retrieve or auto-generate today's Market Pulse
    pulse_obj = await get_or_create_market_pulse(db, market_svc)

    return WhileAwayResponse(
        user_id=target_user_id,
        stats=WhileAwayStats(
            hours_away=round(hours_away, 1),
            total_events=len(scored_events),
            high_impact_events=high,
            medium_impact_events=medium,
            low_impact_events=low,
            last_snapshot_time=latest_snapshot.snapshot_time,
        ),
        events=[EventOut.model_validate(e) for e in db_events],
        pulse=MarketPulseOut.model_validate(pulse_obj) if pulse_obj else None,
    )


@router.get("/pulse", response_model=MarketPulseOut)
async def market_pulse(db: AsyncSession = Depends(get_db)):
    """
    Get the Daily Market Pulse.
    If not yet generated today, fetches sector telemetry, queries Gemini API,
    and returns the summarized narrative.
    """
    market_svc = MarketDataService()
    pulse = await get_or_create_market_pulse(db, market_svc)
    return pulse


async def get_or_create_market_pulse(db: AsyncSession, market_svc: MarketDataService) -> MarketPulse:
    """Helper to return cached pulse or generate a fresh one."""
    today = date.today()
    today_str = today.isoformat()

    # 1. Check Redis cache first
    cached_pulse = await cache.get(pulse_key(today_str))
    if cached_pulse:
        return MarketPulse(**cached_pulse)

    # 2. Check Database
    result = await db.execute(
        select(MarketPulse).where(MarketPulse.pulse_date == today)
    )
    pulse = result.scalar_one_or_none()
    if pulse:
        return pulse

    # 3. Generate fresh Market Pulse
    sector_data = await market_svc.get_sector_performance()
    pulse_gen = MarketPulseGenerator()
    generated = await pulse_gen.generate_pulse(sector_data)

    pulse = MarketPulse(
        pulse_date=today,
        market_mood=generated.get("market_mood", "Bullish"),
        strongest_sector=generated.get("strongest_sector", "Auto & EV"),
        weakest_sector=generated.get("weakest_sector", "Pharma"),
        top_theme=generated.get("top_theme", "EV Momentum"),
        global_sentiment=generated.get("global_sentiment", "Bullish"),
        summary=f"Strongest sector: {generated.get('strongest_sector')}. Weakest: {generated.get('weakest_sector')}.",
        ai_narrative=generated.get("ai_narrative", ""),
        raw_data=generated.get("raw_data", {}),
    )
    db.add(pulse)
    await db.flush()

    # Cache in Redis
    await cache.set(pulse_key(today_str), {
        "id": str(pulse.id),
        "pulse_date": today_str,
        "market_mood": pulse.market_mood,
        "strongest_sector": pulse.strongest_sector,
        "weakest_sector": pulse.weakest_sector,
        "top_theme": pulse.top_theme,
        "global_sentiment": pulse.global_sentiment,
        "summary": pulse.summary,
        "ai_narrative": pulse.ai_narrative,
    }, ttl=3600)

    return pulse


from datetime import timedelta
