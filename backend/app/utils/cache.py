"""
Redis cache utility for Groww Lens.
Provides resilient caching for market quotes, detected events, and market pulse.
Gracefully degrades if Redis is unavailable.
"""

import json
import logging
from typing import Any, Optional
import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger("groww_lens.cache")

# Cache TTLs (seconds)
TTL_MARKET_DATA = 60       # 1 minute — volatile stock prices
TTL_EVENTS = 300           # 5 minutes — detected events
TTL_MARKET_PULSE = 3600    # 1 hour — daily market pulse
TTL_IMPACT_SCORE = 300     # 5 minutes — scored events


class CacheClient:
    """Async Redis cache client with automatic fault-tolerance."""

    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self._is_connected: bool = False

    async def connect(self):
        """Initialize Redis connection pool."""
        try:
            self._client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            await self._client.ping()
            self._is_connected = True
            logger.info("Connected to Redis cache at %s", settings.REDIS_URL)
        except Exception as err:
            self._is_connected = False
            logger.warning("Redis not available (%s). Caching disabled; running in direct-fetch mode.", err)

    async def disconnect(self):
        """Close Redis connection."""
        if self._client:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._is_connected = False

    async def get(self, key: str) -> Optional[Any]:
        """Get parsed JSON value from cache."""
        if not self._is_connected or not self._client:
            return None
        try:
            val = await self._client.get(key)
            return json.loads(val) if val else None
        except Exception as err:
            logger.debug("Cache get error for key %s: %s", key, err)
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Store value as JSON with expiration TTL."""
        if not self._is_connected or not self._client:
            return False
        try:
            await self._client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as err:
            logger.debug("Cache set error for key %s: %s", key, err)
            return False

    async def delete(self, key: str) -> bool:
        """Evict key from cache."""
        if not self._is_connected or not self._client:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception as err:
            logger.debug("Cache delete error for key %s: %s", key, err)
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self._is_connected or not self._client:
            return False
        try:
            return bool(await self._client.exists(key))
        except Exception:
            return False

    @property
    def is_connected(self) -> bool:
        return self._is_connected


# Helper functions to generate standardized cache keys
def market_data_key(symbol: str) -> str:
    return f"groww:quote:{symbol.upper()}"


def events_key(user_id: str) -> str:
    return f"groww:events:{user_id}"


def pulse_key(date_str: str) -> str:
    return f"groww:pulse:{date_str}"


# Singleton instance
cache = CacheClient()
