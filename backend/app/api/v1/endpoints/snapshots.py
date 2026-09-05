"""
Snapshots endpoints — create and retrieve market snapshots.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.database.session import get_db
from app.models.models import Snapshot, SnapshotItem, WatchlistItem, Watchlist
from app.schemas.schemas import SnapshotCreate, SnapshotOut, MessageResponse
from app.services.market_data import MarketDataService

router = APIRouter()


@router.post("/create", response_model=SnapshotOut, status_code=201)
async def create_snapshot(payload: SnapshotCreate, db: AsyncSession = Depends(get_db)):
    """
    Capture a market snapshot for a user.
    Fetches current prices for all stocks in all user watchlists.
    """
    # Get all unique symbols across all user watchlists
    result = await db.execute(
        select(WatchlistItem.symbol, WatchlistItem.company_name)
        .join(Watchlist, WatchlistItem.watchlist_id == Watchlist.id)
        .where(Watchlist.user_id == payload.user_id)
        .distinct()
    )
    rows = result.all()
    if not rows:
        raise HTTPException(status_code=400, detail="User has no stocks in any watchlist")

    # Create snapshot record
    snapshot = Snapshot(user_id=payload.user_id, trigger_type=payload.trigger_type)
    db.add(snapshot)
    await db.flush()

    # Fetch market data
    market_svc = MarketDataService()
    symbols = [row.symbol for row in rows]
    symbol_to_company = {row.symbol: row.company_name for row in rows}

    quotes = await market_svc.get_quotes(symbols)

    # Persist snapshot items
    snapshot_items = []
    for symbol, quote in quotes.items():
        item = SnapshotItem(
            snapshot_id=snapshot.id,
            symbol=symbol,
            company_name=symbol_to_company.get(symbol, quote.get("company_name", symbol)),
            price=quote["price"],
            daily_change=quote["daily_change"],
            daily_change_abs=quote.get("daily_change_abs"),
            volume=quote["volume"],
            avg_volume=quote.get("avg_volume"),
            market_cap=quote.get("market_cap"),
            high_52w=quote.get("high_52w"),
            low_52w=quote.get("low_52w"),
        )
        db.add(item)
        snapshot_items.append(item)

    await db.flush()
    await db.refresh(snapshot)
    return snapshot


@router.get("/latest", response_model=SnapshotOut)
async def get_latest_snapshot(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get the most recent snapshot for a user."""
    result = await db.execute(
        select(Snapshot)
        .where(Snapshot.user_id == user_id)
        .order_by(Snapshot.snapshot_time.desc())
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshots found for this user")

    # Load items
    items_result = await db.execute(
        select(SnapshotItem).where(SnapshotItem.snapshot_id == snapshot.id)
    )
    snapshot.items = items_result.scalars().all()
    return snapshot


@router.get("/", response_model=list[SnapshotOut])
async def list_snapshots(user_id: UUID, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """List recent snapshots for a user."""
    result = await db.execute(
        select(Snapshot)
        .where(Snapshot.user_id == user_id)
        .order_by(Snapshot.snapshot_time.desc())
        .limit(limit)
    )
    return result.scalars().all()
