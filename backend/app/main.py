"""
Groww Lens — FastAPI Application Entry Point
Production-ready configuration with CORS, Redis lifecycle, and API routing.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.database.session import engine, Base
from app.api.v1.router import api_router
from app.utils.cache import cache

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("groww_lens")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("🔭 Starting Groww Lens API (Environment: %s)...", settings.ENVIRONMENT)

    # 1. Connect to Redis cache (non-blocking, graceful fallback)
    await cache.connect()

    # 2. Ensure database tables exist (development convenience)
    if settings.ENVIRONMENT == "development":
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables verified and ready")
        except Exception as err:
            logger.warning("Database table creation notice: %s", err)

    yield

    # Shutdown
    logger.info("👋 Shutting down Groww Lens API...")
    await cache.disconnect()
    await engine.dispose()
    logger.info("Connections released.")


app = FastAPI(
    title="Groww Lens API",
    description="Your Market Memory — Smart Watchlist with AI-powered change detection and impact scoring",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "Groww Lens",
        "tagline": "Your Market Memory",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "cache_connected": cache.is_connected,
    }
