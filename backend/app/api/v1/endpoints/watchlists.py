"""
Watchlists endpoints — CRUD for watchlists and their stock items.
Supports both user_id query/body parameters with demo user fallback.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.database.session import get_db
from app.models.models import Watchlist, WatchlistItem, User
from app.schemas.schemas import (
    WatchlistCreate, WatchlistOut,
    WatchlistItemAdd, WatchlistItemOut,
    MessageResponse,
)
from app.services.market_data import MarketDataService

router = APIRouter()

DEFAULT_DEMO_USER_ID = UUID("a0000000-0000-0000-0000-000000000001")


async def ensure_user_exists(db: AsyncSession, user_id: UUID) -> User:
    """Ensure user exists in DB before attaching watchlist."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        # Auto-create demo user if referencing default demo ID
        if user_id == DEFAULT_DEMO_USER_ID:
            user = User(
                id=DEFAULT_DEMO_USER_ID,
                name="Demo User",
                email="demo@growwlens.in",
            )
            db.add(user)
            await db.flush()
        else:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return user


# ─── Watchlist CRUD ───────────────────────────────────────────────────────────

@router.post("/", response_model=WatchlistOut, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    payload: WatchlistCreate,
    user_id: Optional[UUID] = Query(None, description="User ID (defaults to demo user)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new watchlist.
    User ID can be provided in query parameter, request body, or defaults to demo user.
    """
    target_user_id = user_id or payload.user_id or DEFAULT_DEMO_USER_ID
    await ensure_user_exists(db, target_user_id)

    watchlist = Watchlist(
        user_id=target_user_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(watchlist)
    await db.flush()
    await db.refresh(watchlist)

    result = WatchlistOut.model_validate(watchlist)
    result.item_count = 0
    return result


@router.get("/", response_model=List[WatchlistOut])
async def list_watchlists(
    user_id: Optional[UUID] = Query(DEFAULT_DEMO_USER_ID, description="Filter watchlists by user ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    List all watchlists for a user, including total stock counts.
    Defaults to demo user if no user_id is passed.
    """
    stmt = (
        select(Watchlist, func.count(WatchlistItem.id).label("item_count"))
        .outerjoin(WatchlistItem, Watchlist.id == WatchlistItem.watchlist_id)
        .where(Watchlist.user_id == user_id)
        .group_by(Watchlist.id)
        .order_by(Watchlist.created_at.desc())
    )
    rows = await db.execute(stmt)
    results = []
    for watchlist, count in rows.all():
        out = WatchlistOut.model_validate(watchlist)
        out.item_count = count
        results.append(out)
    return results


@router.delete("/{watchlist_id}", response_model=MessageResponse)
async def delete_watchlist(
    watchlist_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a watchlist and all its associated stocks."""
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    await db.delete(watchlist)
    return {"message": f"Watchlist '{watchlist.name}' deleted successfully", "success": True}


# ─── Watchlist Stocks CRUD ────────────────────────────────────────────────────

@router.post("/{watchlist_id}/stocks", response_model=WatchlistItemOut, status_code=status.HTTP_201_CREATED)
async def add_stock(
    watchlist_id: UUID,
    payload: WatchlistItemAdd,
    db: AsyncSession = Depends(get_db),
):
    """Add a stock symbol to a specific watchlist."""
    # Verify watchlist exists
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Watchlist not found")

    symbol_clean = payload.symbol.strip().upper()

    # Prevent duplicate stocks in same watchlist
    existing = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.symbol == symbol_clean,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Stock {symbol_clean} is already in this watchlist")

    item = WatchlistItem(
        watchlist_id=watchlist_id,
        symbol=symbol_clean,
        company_name=payload.company_name.strip(),
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)

    out = WatchlistItemOut.model_validate(item)
    try:
        quotes = await MarketDataService().get_quotes([symbol_clean])
        q = quotes.get(symbol_clean)
        if q and isinstance(q, dict):
            out.price = q.get("price")
            out.daily_change = q.get("daily_change")
            out.daily_change_abs = q.get("daily_change_abs")
            out.volume = q.get("volume")
            out.avg_volume = q.get("avg_volume")
    except Exception:
        pass
    return out


@router.get("/{watchlist_id}/stocks", response_model=List[WatchlistItemOut])
async def list_stocks(
    watchlist_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """List all stock items belonging to a watchlist with real-time market data."""
    # Verify watchlist exists
    result = await db.execute(select(Watchlist).where(Watchlist.id == watchlist_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Watchlist not found")

    result = await db.execute(
        select(WatchlistItem)
        .where(WatchlistItem.watchlist_id == watchlist_id)
        .order_by(WatchlistItem.added_at.asc())
    )
    items = result.scalars().all()
    if not items:
        return []

    symbols = [it.symbol for it in items]
    quotes_map = {}
    try:
        quotes_map = await MarketDataService().get_quotes(symbols)
    except Exception:
        quotes_map = {}

    out_items = []
    for it in items:
        out = WatchlistItemOut.model_validate(it)
        q = quotes_map.get(it.symbol)
        if q and isinstance(q, dict):
            out.price = q.get("price")
            out.daily_change = q.get("daily_change")
            out.daily_change_abs = q.get("daily_change_abs")
            out.volume = q.get("volume")
            out.avg_volume = q.get("avg_volume")
        out_items.append(out)

    return out_items


@router.delete("/{watchlist_id}/stocks/{symbol}", response_model=MessageResponse)
async def remove_stock(
    watchlist_id: UUID,
    symbol: str,
    db: AsyncSession = Depends(get_db),
):
    """Remove a stock from a watchlist by its symbol."""
    symbol_clean = symbol.strip().upper()
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.symbol == symbol_clean,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail=f"Stock {symbol_clean} not found in watchlist")

    await db.delete(item)
    return {"message": f"{symbol_clean} removed from watchlist", "success": True}
