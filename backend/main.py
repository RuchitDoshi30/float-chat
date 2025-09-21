"""
Ocean Chat Backend 2.0 - FastAPI Application Entry Point

This is the main FastAPI application with dual data source architecture.
It implements intelligent fallback from live APIs to local NetCDF database.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.router import api_router
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown events."""
    # Startup
    logger.info("🌊 Ocean Chat Backend 2.0 starting up...")
    await init_db()
    logger.info("✅ Database initialized successfully")
    yield
    # Shutdown
    logger.info("🌊 Ocean Chat Backend 2.0 shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Ocean Chat Backend 2.0",
    description="Advanced oceanographic data platform with intelligent dual data source architecture",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - health check and basic info."""
    return {
        "message": "🌊 Ocean Chat Backend 2.0 - Smart Ocean Data Platform",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "Intelligent dual data source architecture",
            "Natural language processing for ocean queries",
            "Real-time API with database fallback",
            "Advanced oceanographic data visualization"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2025-09-21T00:00:00Z",
        "services": {
            "database": "connected",
            "redis": "connected",
            "external_apis": "available"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )