"""
Health check endpoint — for Docker health checks and monitoring.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_settings
from app.core.database import get_db
from app.core.redis import get_redis

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check endpoint.
    Checks: API, Database, Redis connectivity.
    """
    settings = get_settings()
    health = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "services": {},
    }

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        health["services"]["database"] = {"status": "healthy"}
    except Exception as e:
        health["services"]["database"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"

    # Redis check
    try:
        redis = await get_redis()
        await redis.ping()
        health["services"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health["services"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "degraded"

    return health
