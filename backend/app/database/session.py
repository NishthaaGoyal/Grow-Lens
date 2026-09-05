"""
SQLAlchemy async database session and engine setup.
Supports PostgreSQL (asyncpg) with proper connection pooling and pre-ping.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

import re
import urllib.parse
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL.strip()

# Normalize scheme for asyncpg
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Check if SQLite or PostgreSQL
is_sqlite = DATABASE_URL.startswith("sqlite")
is_supabase = "supabase.co" in DATABASE_URL or "pooler.supabase.com" in DATABASE_URL
is_pooler = "pooler.supabase.com" in DATABASE_URL or ":6543" in DATABASE_URL

# Sanitize query parameters that asyncpg doesn't accept as URL query args (e.g. sslmode)
if not is_sqlite and "asyncpg" in DATABASE_URL:
    # Strip ?sslmode=... or &sslmode=... from URL since asyncpg receives ssl via connect_args
    DATABASE_URL = re.sub(r'[?&]sslmode=[^&]*', '', DATABASE_URL)
    if '?' in DATABASE_URL and DATABASE_URL.endswith('?'):
        DATABASE_URL = DATABASE_URL[:-1]

engine_kwargs = {
    "echo": settings.DEBUG,
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = NullPool
else:
    # PostgreSQL / Supabase configuration
    connect_args = {
        # Required for Supabase transaction pooler (port 6543 / PgBouncer / Supavisor)
        "statement_cache_size": 0,
    }
    if is_supabase or "ssl" in settings.DATABASE_URL.lower():
        connect_args["ssl"] = "require"

    engine_kwargs["connect_args"] = connect_args

    if is_pooler:
        # Supabase transaction pooler manages pooling remotely
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency: yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
