"""Database setup and session management."""

from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base

from .config import get_settings

# Settings
settings = get_settings()

# SQLAlchemy setup with database-specific configuration
database_url = str(settings.database_url)

if database_url.startswith("sqlite"):
    # SQLite configuration
    engine = create_async_engine(
        database_url,
        echo=settings.debug,
        # SQLite-specific settings
        pool_pre_ping=False,  # Not needed for file-based DB
        connect_args={"check_same_thread": False},  # Allow multi-threading
    )
else:
    # PostgreSQL or other database configuration
    engine = create_async_engine(
        database_url,
        echo=settings.debug,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=300,
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
metadata = MetaData()
Base = declarative_base(metadata=metadata)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Import models to ensure they're registered
        from . import models  # noqa: F401
        
        # Create tables (checkfirst=True is default and handles conflicts properly)
        await conn.run_sync(metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()