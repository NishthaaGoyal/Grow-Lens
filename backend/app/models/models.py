"""
SQLAlchemy ORM models for all database tables in Groww Lens.
Production-ready with SQLAlchemy 2.0 types and bidirectional relationships.
"""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Integer, Boolean,
    DateTime, Date as SaDate, Numeric, BigInteger, ForeignKey, JSON, CheckConstraint, UniqueConstraint,
    Uuid, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    snapshots = relationship("Snapshot", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan", lazy="selectin")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan", lazy="selectin")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    watchlist_id = Column(Uuid, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("watchlist_id", "symbol", name="uq_watchlist_symbol"),
    )

    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    trigger_type = Column(String(50), nullable=False, default="manual")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="snapshots")
    items = relationship("SnapshotItem", back_populates="snapshot", cascade="all, delete-orphan", lazy="selectin")


class SnapshotItem(Base):
    __tablename__ = "snapshot_items"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(Uuid, ForeignKey("snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    price = Column(Numeric(18, 4), nullable=False)
    daily_change = Column(Numeric(8, 4), nullable=False)       # percentage
    daily_change_abs = Column(Numeric(18, 4), nullable=True)   # absolute value
    volume = Column(BigInteger, nullable=False)
    avg_volume = Column(BigInteger, nullable=True)             # 30-day average
    market_cap = Column(BigInteger, nullable=True)
    high_52w = Column(Numeric(18, 4), nullable=True)
    low_52w = Column(Numeric(18, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    snapshot = relationship("Snapshot", back_populates="items")


class Event(Base):
    __tablename__ = "events"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    event_type = Column(String(100), nullable=False)
    impact_score = Column(Integer, nullable=False, index=True)
    summary = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)                  # AI "Why it matters"
    price_change = Column(Numeric(8, 4), nullable=True)
    volume_ratio = Column(Numeric(8, 2), nullable=True)
    event_metadata = Column("metadata", JSON, default=dict)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        CheckConstraint("impact_score >= 0 AND impact_score <= 100", name="chk_impact_score_range"),
    )

    # Relationships
    user = relationship("User", back_populates="events")


class MarketPulse(Base):
    __tablename__ = "market_pulse"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    pulse_date = Column(SaDate, unique=True, nullable=False, index=True)
    market_mood = Column(String(50), nullable=True)
    strongest_sector = Column(String(100), nullable=True)
    weakest_sector = Column(String(100), nullable=True)
    top_theme = Column(String(255), nullable=True)
    global_sentiment = Column(String(50), nullable=True)
    summary = Column(Text, nullable=True)
    ai_narrative = Column(Text, nullable=True)
    raw_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NewsCache(Base):
    __tablename__ = "news_cache"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    symbol = Column(String(50), nullable=True, index=True)
    headline = Column(Text, nullable=False)
    source = Column(String(255), nullable=True)
    url = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    sentiment = Column(String(20), nullable=True)
    sentiment_score = Column(Numeric(5, 4), nullable=True)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now())
