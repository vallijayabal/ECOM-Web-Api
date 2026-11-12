"""
FastAPI Application Entry Point
================================
Enterprise E-Commerce Platform API

Initializes the FastAPI application with:
- Middleware stack (CORS, audit logging, request timing)
- Exception handlers
- API routers
- Startup/shutdown lifecycle hooks
- Swagger/ReDoc documentation
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.core import get_settings
from app.core.database import close_db, init_db
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    general_exception_handler,
    http_exception_handler,
)
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.core.redis import close_redis
from app.api.v1.router import api_v1_router


settings = get_settings()


# ═══════════════════════════════════════════════════
# Application Lifespan
# ═══════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──
    setup_logging()

    from app.core.logging import get_logger
    logger = get_logger("startup")
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )

    # Initialize database
    await init_db()
    logger.info("database_initialized")

    # Store settings on app state for middleware access
    app.state.settings = settings

    logger.info("application_started", port=settings.APP_PORT)

    yield  # Application runs

    # ── Shutdown ──
    logger.info("application_shutting_down")
    await close_db()
    await close_redis()
    logger.info("application_stopped")


# ═══════════════════════════════════════════════════
# FastAPI Application
# ═══════════════════════════════════════════════════

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Enterprise-grade E-Commerce Platform API. "
        "Supports multi-tenant, multi-store architecture with "
        "comprehensive product, order, and payment management."
    ),
    docs_url="/docs" if settings.IS_DEVELOPMENT else None,
    redoc_url="/redoc" if settings.IS_DEVELOPMENT else None,
    openapi_url="/openapi.json" if settings.IS_DEVELOPMENT else None,
    lifespan=lifespan,
)


# ── Middleware ──
setup_middleware(app)


# ── Exception Handlers ──
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# ── API Routers ──
app.include_router(api_v1_router)


# ── Root Endpoint ──
@app.get("/", tags=["Root"])
async def root():
    """API root — returns basic info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "docs": "/docs" if settings.IS_DEVELOPMENT else "disabled",
        "health": "/api/v1/health",
    }
