"""
Seed script — populates the database with demo data for the hackathon.
Run with: python seed.py

This creates:
- 1 demo user
- 2 watchlists (Technology + Auto & EV)
- 6 stocks
- 1 snapshot with mock prices
- Demo events showing the "While You Were Away" experience
"""

import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta
from uuid import UUID
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.session import AsyncSessionLocal, engine, Base
from app.models.models import (
    User, Watchlist, WatchlistItem,
    Snapshot, SnapshotItem, Event, MarketPulse
)
from sqlalchemy import select


DEMO_STOCKS = {
    "Technology": [
        {"symbol": "INFY.NS",  "company_name": "Infosys Limited"},
        {"symbol": "TCS.NS",   "company_name": "Tata Consultancy Services"},
        {"symbol": "WIPRO.NS", "company_name": "Wipro Limited"},
    ],
    "Auto & EV": [
        {"symbol": "TATAMOTORS.NS", "company_name": "Tata Motors Limited"},
        {"symbol": "M&M.NS",        "company_name": "Mahindra & Mahindra"},
        {"symbol": "OLECTRA.NS",    "company_name": "Olectra Greentech"},
    ],
}

BASE_PRICES = {
    "INFY.NS": 1820.0,
    "TCS.NS": 4080.0,
    "WIPRO.NS": 475.0,
    "TATAMOTORS.NS": 830.0,
    "M&M.NS": 3050.0,
    "OLECTRA.NS": 1390.0,
}

# Simulate the "while you were away" scenario with dramatic changes
DEMO_CHANGES = {
    "TATAMOTORS.NS": {"pct": +4.8, "volume_ratio": 2.9, "event": "price_surge",
                       "news": "Quarterly sales announcement released with record EV numbers"},
    "INFY.NS":       {"pct": +2.3, "volume_ratio": 1.8, "event": "price_surge",
                       "news": "Large enterprise client deal announced"},
    "TCS.NS":        {"pct": -0.9, "volume_ratio": 0.9, "event": "minor_fluctuation",
                       "news": ""},
    "WIPRO.NS":      {"pct": +1.1, "volume_ratio": 1.2, "event": "minor_fluctuation",
                       "news": ""},
    "M&M.NS":        {"pct": +3.2, "volume_ratio": 2.1, "event": "price_surge",
                       "news": "New EV model launch event announced"},
    "OLECTRA.NS":    {"pct": +6.5, "volume_ratio": 4.2, "event": "price_surge",
                       "news": "₹500Cr government order secured"},
}

DEMO_USER_ID = "a0000000-0000-0000-0000-000000000001"


async def seed():
    print("🌱 Seeding Groww Lens demo data...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # ── Demo User ──────────────────────────────────────────────────────
        result = await db.execute(select(User).where(User.email == "demo@growwlens.in"))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                id=UUID(DEMO_USER_ID),
                name="Demo User",
                email="demo@growwlens.in",
            )
            db.add(user)
            await db.flush()
            print(f"  ✅ Created demo user: {user.email}")
        else:
            print(f"  ⏭  Demo user already exists: {user.email}")

        # ── Watchlists ─────────────────────────────────────────────────────
        for watchlist_name, stocks in DEMO_STOCKS.items():
            result = await db.execute(
                select(Watchlist).where(
                    Watchlist.user_id == user.id,
                    Watchlist.name == watchlist_name,
                )
            )
            watchlist = result.scalar_one_or_none()
            if not watchlist:
                watchlist = Watchlist(user_id=user.id, name=watchlist_name)
                db.add(watchlist)
                await db.flush()
                print(f"  ✅ Created watchlist: {watchlist_name}")

                for stock in stocks:
                    item = WatchlistItem(
                        watchlist_id=watchlist.id,
                        symbol=stock["symbol"],
                        company_name=stock["company_name"],
                    )
                    db.add(item)
                print(f"     Added {len(stocks)} stocks to {watchlist_name}")
            else:
                print(f"  ⏭  Watchlist exists: {watchlist_name}")

        await db.flush()

        # ── Snapshot (12 hours ago) ────────────────────────────────────────
        snapshot_time = datetime.now(timezone.utc) - timedelta(hours=12)
        snapshot = Snapshot(
            user_id=user.id,
            snapshot_time=snapshot_time,
            trigger_type="session_exit",
        )
        db.add(snapshot)
        await db.flush()
        print(f"  ✅ Created snapshot at {snapshot_time.strftime('%H:%M UTC')}")

        for symbol, base_price in BASE_PRICES.items():
            company_name = next(
                s["company_name"]
                for stocks in DEMO_STOCKS.values()
                for s in stocks
                if s["symbol"] == symbol
            )
            avg_vol = random.randint(1_000_000, 3_000_000)
            snap_item = SnapshotItem(
                snapshot_id=snapshot.id,
                symbol=symbol,
                company_name=company_name,
                price=base_price,
                daily_change=round(random.uniform(-1.5, 1.5), 4),
                volume=int(avg_vol * random.uniform(0.8, 1.2)),
                avg_volume=avg_vol,
            )
            db.add(snap_item)

        await db.flush()
        print("  ✅ Snapshot items saved")

        # ── Demo Events ────────────────────────────────────────────────────
        event_scores = {
            "OLECTRA.NS": 94,
            "TATAMOTORS.NS": 91,
            "M&M.NS": 79,
            "INFY.NS": 76,
            "WIPRO.NS": 22,
            "TCS.NS": 12,
        }

        explanations = {
            "OLECTRA.NS": (
                "Olectra has surged 6.5% on very high trading volume (4.2x average), "
                "driven by a major government bus order worth ₹500 crore. "
                "This kind of institutional order significantly boosts future revenue visibility."
            ),
            "TATAMOTORS.NS": (
                "Tata Motors gained 4.8% with nearly 3x normal trading activity, "
                "backed by a strong quarterly sales announcement with record EV deliveries. "
                "High volume alongside positive news typically signals genuine investor conviction."
            ),
            "M&M.NS": (
                "Mahindra & Mahindra rose 3.2% ahead of a new electric vehicle model launch event. "
                "EV-related news has been drawing significant investor interest across the sector. "
                "The 2.1x volume supports the move as more than routine trading."
            ),
            "INFY.NS": (
                "Infosys gained 2.3% following the announcement of a large enterprise client contract. "
                "Such deals typically improve future revenue expectations and can positively "
                "influence investor sentiment over the coming weeks."
            ),
            "WIPRO.NS": "Wipro saw a minor 1.1% uptick with no significant news catalyst — likely sector momentum.",
            "TCS.NS": "TCS showed a small decline of 0.9% on light volume. No notable event detected.",
        }

        for symbol, change_data in DEMO_CHANGES.items():
            company_name = next(
                s["company_name"]
                for stocks in DEMO_STOCKS.values()
                for s in stocks
                if s["symbol"] == symbol
            )
            base = BASE_PRICES[symbol]
            current = base * (1 + change_data["pct"] / 100)

            direction = "gained" if change_data["pct"] > 0 else "dropped"
            news_suffix = f". {change_data['news']}" if change_data["news"] else ""

            event = Event(
                user_id=user.id,
                symbol=symbol,
                company_name=company_name,
                event_type=change_data["event"],
                impact_score=event_scores[symbol],
                summary=(
                    f"{company_name} {direction} {abs(change_data['pct']):.1f}% since your last visit "
                    f"(₹{base:.0f} → ₹{current:.0f}){news_suffix}"
                ),
                explanation=explanations[symbol],
                price_change=change_data["pct"],
                volume_ratio=change_data["volume_ratio"],
                event_metadata={
                    "snapshot_price": base,
                    "current_price": round(current, 2),
                    "volume_ratio": change_data["volume_ratio"],
                },
                is_read=False,
            )
            db.add(event)

        await db.flush()
        print(f"  ✅ Created {len(DEMO_CHANGES)} demo events")

        # ── Market Pulse ───────────────────────────────────────────────────
        from datetime import date
        today = date.today()
        result = await db.execute(select(MarketPulse).where(MarketPulse.pulse_date == today))
        if not result.scalar_one_or_none():
            pulse = MarketPulse(
                pulse_date=today,
                market_mood="Bullish",
                strongest_sector="Auto & EV",
                weakest_sector="Pharma",
                top_theme="EV Stocks",
                global_sentiment="Bullish",
                summary="Auto and EV sectors are driving today's rally as government policy tailwinds continue.",
                ai_narrative=(
                    "Indian markets are showing broad-based optimism today, led by the Auto & EV sector "
                    "which continues to benefit from policy support and rising consumer demand for electric vehicles. "
                    "Pharma stocks are under mild pressure following global pricing concerns."
                ),
                raw_data={
                    "sectors": {
                        "Technology": +0.8, "Auto & EV": +3.1,
                        "Banking": +0.4, "Pharma": -0.6,
                        "FMCG": +0.2, "Energy": +1.1,
                    }
                },
            )
            db.add(pulse)
            await db.flush()
            print("  ✅ Created today's Market Pulse")

        await db.commit()
        print("\n🎉 Seed complete! Demo data ready.")
        print(f"   Demo user ID: {DEMO_USER_ID}")
        print(f"   API: http://localhost:8000/docs")
        print(f"   Try: GET /api/v1/dashboard/while-away?user_id={DEMO_USER_ID}")


if __name__ == "__main__":
    asyncio.run(seed())
