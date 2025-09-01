"""Main FastAPI application for mem8 backend API."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .config import get_settings
from .database import init_db, close_db
from .routers import thoughts, search, sync, teams, health, auth, public
# from .websocket import websocket_endpoint

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    settings = get_settings()
    
    # Initialize database (works properly with PostgreSQL)
    logger.info("Initializing database...")
    await init_db()
    
    logger.info(f"mem8 API starting on {settings.host}:{settings.port}")
    yield
    
    # Cleanup
    logger.info("Shutting down mem8 API...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="mem8 API",
    description="Backend API for AI Memory Management and team collaboration",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.allowed_hosts,
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(public.router, prefix="/api/v1/public", tags=["public"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(
    thoughts.router,
    prefix="/api/v1",
    tags=["thoughts"]
)
app.include_router(
    search.router,
    prefix="/api/v1", 
    tags=["search"]
)
app.include_router(
    sync.router,
    prefix="/api/v1",
    tags=["sync"]
)
app.include_router(
    teams.router,
    prefix="/api/v1",
    tags=["teams"]
)


@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "mem8 API",
        "version": "0.1.0",
        "docs": "/docs"
    }