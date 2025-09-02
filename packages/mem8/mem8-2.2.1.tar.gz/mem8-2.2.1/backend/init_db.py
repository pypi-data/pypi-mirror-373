#!/usr/bin/env python3
"""Initialize the database."""

import asyncio
import logging
from sqlalchemy import text

from src.mem8_api.database import engine, metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    """Initialize database with tables."""
    logger.info("Creating SQLite database...")
    
    async with engine.begin() as conn:
        # Import models to ensure they're registered
        from src.mem8_api import models  # noqa: F401
        
        # Drop all existing tables to avoid conflicts
        await conn.run_sync(metadata.drop_all)
        logger.info("Dropped existing tables")
        
        # Create all tables fresh
        await conn.run_sync(metadata.create_all)
        logger.info("Created all tables")
        
        # Verify database is working
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = result.fetchall()
        logger.info("Created tables: %s", [table[0] for table in tables])

if __name__ == "__main__":
    asyncio.run(init_database())