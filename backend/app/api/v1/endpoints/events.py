"""
Events endpoints — retrieve detected market events.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from uuid import UUID

from app.database.session import get_db
from app.models.models import Event
from app.schemas.schemas import EventOut, EventMarkRead, MessageResponse
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[EventOut])
async def list_events(
    user_id: UUID,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """List all events for a user, sorted by impact score."""
    stmt = (
        select(Event)
        .where(Event.user_id == user_id)
        .order_by(Event.impact_score.desc(), Event.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if unread_only:
        stmt = stmt.where(Event.is_read == False)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/high-impact", response_model=List[EventOut])
async def list_high_impact_events(
    user_id: UUID,
    threshold: int = Query(settings.HIGH_IMPACT_THRESHOLD, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List only high-impact events (score >= threshold)."""
    result = await db.execute(
        select(Event)
        .where(Event.user_id == user_id, Event.impact_score >= threshold)
        .order_by(Event.impact_score.desc())
    )
    return result.scalars().all()


@router.post("/mark-read", response_model=MessageResponse)
async def mark_events_read(payload: EventMarkRead, db: AsyncSession = Depends(get_db)):
    """Mark specific events as read."""
    await db.execute(
        update(Event)
        .where(Event.id.in_(payload.event_ids))
        .values(is_read=True)
    )
    return {"message": f"{len(payload.event_ids)} events marked as read", "success": True}


@router.get("/{event_id}", response_model=EventOut)
async def get_event(event_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single event by ID."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")
    return event
