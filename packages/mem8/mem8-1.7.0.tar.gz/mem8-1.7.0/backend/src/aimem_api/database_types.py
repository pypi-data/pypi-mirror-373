"""Database type utilities for cross-database compatibility."""

import os
from sqlalchemy import String, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgresUUID

# Determine database type from environment or default to SQLite
database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./mem8.db")

# Choose appropriate types based on database
if database_url.startswith("postgresql"):
    JsonType = JSONB
    UuidType = PostgresUUID(as_uuid=False)  # Store as string for compatibility
else:
    # SQLite and other databases
    JsonType = JSON
    UuidType = String(36)  # UUID as string for SQLite