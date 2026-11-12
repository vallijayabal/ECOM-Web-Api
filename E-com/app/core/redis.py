"""
Redis connection management.
Provides async Redis client with connection pooling.
"""

from typing import Optional

import redis.asyncio as aioredis

from app.core import get_settings

settings = get_settings()

# Module-level client reference
_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get or create Redis client (singleton)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
    return _redis_client


async def close_redis() -> None:
    """Close Redis connection pool."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None


class CacheService:
    """High-level caching operations."""

    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def get(self, key: str) -> Optional[str]:
        """Get cached value by key."""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        """Set cached value with TTL (default 5 minutes)."""
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> None:
        """Delete cached value."""
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching pattern."""
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return bool(await self.redis.exists(key))

    async def increment(self, key: str) -> int:
        """Increment a counter."""
        return await self.redis.incr(key)

    async def get_json(self, key: str) -> Optional[dict]:
        """Get cached JSON value."""
        import json
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(self, key: str, value: dict, ttl: int = 300) -> None:
        """Set cached JSON value with TTL."""
        import json
        await self.redis.setex(key, ttl, json.dumps(value, default=str))
