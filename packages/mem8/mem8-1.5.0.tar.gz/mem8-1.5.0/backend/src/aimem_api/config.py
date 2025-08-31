"""Configuration management for AI-Mem API."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Security settings
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )
    
    # CORS settings
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
        description="Allowed CORS origins"
    )
    allowed_hosts: List[str] = Field(
        default=["*"],
        description="Allowed host headers"
    )
    
    # Database settings
    # Default: PostgreSQL for Docker/cloud-friendly deployment
    # Fallback: SQLite for local development without Docker
    database_url: str = Field(
        default="postgresql+asyncpg://aimem_user:aimem_password@localhost:5432/aimem",
        description="Database connection URL (PostgreSQL by default, SQLite fallback for local dev)"
    )
    
    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL"
    )
    
    # Search settings
    search_model_name: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model name"
    )
    
    # File upload settings
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size in bytes"
    )
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    
    # GitHub OAuth settings
    github_client_id: str = Field(
        default="",
        description="GitHub OAuth client ID"
    )
    github_client_secret: str = Field(
        default="",
        description="GitHub OAuth client secret"
    )
    github_redirect_uri: str = Field(
        default="http://localhost:3000/auth/callback",
        description="GitHub OAuth redirect URI"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()