"""
Pydantic schemas for request/response validation.
"""

from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID


# ─────────────────────────────────────────────
# User Schemas
# ─────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class UserOut(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# Watchlist Schemas
# ─────────────────────────────────────────────

class WatchlistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    user_id: Optional[UUID] = None


class WatchlistOut(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    item_count: Optional[int] = 0

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# Watchlist Item Schemas
# ─────────────────────────────────────────────

class WatchlistItemAdd(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=255)


class WatchlistItemOut(BaseModel):
    id: UUID
    watchlist_id: UUID
    symbol: str
    company_name: str
    added_at: datetime
    price: Optional[float] = None
    daily_change: Optional[float] = None
    daily_change_abs: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# Snapshot Schemas
# ─────────────────────────────────────────────

class SnapshotItemData(BaseModel):
    symbol: str
    company_name: str
    price: float
    daily_change: float
    daily_change_abs: Optional[float] = None
    volume: int
    avg_volume: Optional[int] = None
    market_cap: Optional[int] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None


class SnapshotCreate(BaseModel):
    user_id: UUID
    trigger_type: str = "manual"
    items: Optional[List[SnapshotItemData]] = None  # auto-fetched if None


class SnapshotItemOut(BaseModel):
    id: UUID
    snapshot_id: UUID
    symbol: str
    company_name: str
    price: float
    daily_change: float
    volume: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SnapshotOut(BaseModel):
    id: UUID
    user_id: UUID
    snapshot_time: datetime
    trigger_type: str
    items: List[SnapshotItemOut] = []

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# Event Schemas
# ─────────────────────────────────────────────

class EventOut(BaseModel):
    id: UUID
    user_id: UUID
    symbol: str
    company_name: Optional[str] = None
    event_type: str
    impact_score: int
    summary: str
    explanation: Optional[str] = None
    price_change: Optional[float] = None
    volume_ratio: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_read: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_from_orm(cls, data: Any) -> Any:
        if hasattr(data, "event_metadata"):
            return {
                "id": data.id,
                "user_id": data.user_id,
                "symbol": data.symbol,
                "company_name": data.company_name,
                "event_type": data.event_type,
                "impact_score": data.impact_score,
                "summary": data.summary,
                "explanation": data.explanation,
                "price_change": float(data.price_change) if data.price_change is not None else None,
                "volume_ratio": float(data.volume_ratio) if data.volume_ratio is not None else None,
                "metadata": data.event_metadata if isinstance(data.event_metadata, dict) else {},
                "is_read": bool(data.is_read),
                "created_at": data.created_at,
            }
        return data


class EventMarkRead(BaseModel):
    event_ids: List[UUID]


# ─────────────────────────────────────────────
# Market Pulse Schemas
# ─────────────────────────────────────────────

class MarketPulseOut(BaseModel):
    id: UUID
    pulse_date: date
    market_mood: Optional[str]
    strongest_sector: Optional[str]
    weakest_sector: Optional[str]
    top_theme: Optional[str]
    global_sentiment: Optional[str]
    summary: Optional[str]
    ai_narrative: Optional[str]

    model_config = {"from_attributes": True}


# ─────────────────────────────────────────────
# Dashboard Schemas
# ─────────────────────────────────────────────

class WhileAwayStats(BaseModel):
    hours_away: float
    total_events: int
    high_impact_events: int
    medium_impact_events: int
    low_impact_events: int
    last_snapshot_time: Optional[datetime]


class WhileAwayResponse(BaseModel):
    user_id: UUID
    stats: WhileAwayStats
    events: List[EventOut]
    pulse: Optional[MarketPulseOut] = None


class StockQuote(BaseModel):
    symbol: str
    company_name: str
    price: float
    daily_change: float
    daily_change_abs: float
    volume: int
    avg_volume: Optional[int]
    market_cap: Optional[int]
    currency: str = "INR"


# ─────────────────────────────────────────────
# Common / Utility Schemas
# ─────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
