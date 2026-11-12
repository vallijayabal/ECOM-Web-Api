"""
Async database engine and session management using SQLAlchemy 2.0.
Provides connection pooling, async sessions, and dependency injection.
"""

from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core import get_settings

settings = get_settings()

engine = None
async_session_factory = None


async def initialize_engine() -> None:
    """Create the async engine after ensuring the target database exists."""
    global engine, async_session_factory

    if engine is not None and async_session_factory is not None:
        return

    admin_url = (
        f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/mysql?charset=utf8mb4"
    )
    admin_engine = create_async_engine(
        admin_url,
        echo=False,
        pool_pre_ping=True,
    )

    try:
        async with admin_engine.begin() as conn:
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}`"))
    finally:
        await admin_engine.dispose()

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.APP_DEBUG,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=True,
    )
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an async DB session.
    Automatically commits on success and rolls back on error.
    """
    await initialize_engine()
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database (create tables if needed in development).
    """
    await initialize_engine()

    from app.infrastructure.models.base import Base

    if settings.IS_DEVELOPMENT:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Dispose of the database engine.
    """
    if engine is not None:
        await engine.dispose()