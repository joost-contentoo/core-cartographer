"""
Main FastAPI application with CORS, lifecycle management, and route configuration.
"""

import logging
import os
import sys
from pathlib import Path


# Configure Python path for core_cartographer imports
# This handles both local development and Docker production environments
def _configure_python_path():
    """Add core_cartographer to Python path based on environment."""
    possible_paths = [
        Path("/app"),  # Docker production
        # Local dev (relative to this file)
        Path(__file__).parent.parent.parent.parent.parent / "src",
        Path.cwd() / "src",  # Local dev (relative to cwd)
        Path.cwd().parent / "src",  # Running from backend/
    ]

    for base_path in possible_paths:
        if (base_path / "core_cartographer").exists():
            if str(base_path) not in sys.path:
                sys.path.insert(0, str(base_path))
            return

    logging.warning("Could not find core_cartographer package in expected locations")

_configure_python_path()

# Imports after path configuration (intentional E402)
# ruff: noqa: E402
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..cache.file_cache import file_cache
from .routes import analysis, extraction, files

logger = logging.getLogger(__name__)


def _get_cors_origins() -> list[str]:
    """
    Get CORS origins from environment variable or use defaults.

    Set CORS_ORIGINS env var as comma-separated list for production:
    CORS_ORIGINS=https://myapp.com,https://www.myapp.com
    """
    cors_env = os.environ.get("CORS_ORIGINS", "")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    # Default origins for development
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def _validate_api_key():
    """
    Validate that ANTHROPIC_API_KEY is set.
    Logs a warning but doesn't fail - allows health checks to work.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        logger.warning(
            "ANTHROPIC_API_KEY not set. Extraction endpoints will fail. "
            "Set the environment variable to enable Claude API calls."
        )
        return False
    if len(api_key) < 20:
        logger.warning("ANTHROPIC_API_KEY appears invalid (too short).")
        return False
    logger.info("ANTHROPIC_API_KEY validated successfully.")
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown tasks including cache cleanup.
    """
    # Startup validation
    _validate_api_key()

    # Clean expired cache
    file_cache.cleanup_expired()

    # Background task to clean cache every 30 minutes
    async def cleanup_task():
        while True:
            await asyncio.sleep(1800)  # 30 minutes
            file_cache.cleanup_expired()

    task = asyncio.create_task(cleanup_task())

    yield

    # Shutdown: cancel cleanup task
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Core Cartographer API",
    version="1.0.0",
    description="API for extracting localization rules and guidelines from client documentation",
    lifespan=lifespan
)

# CORS configuration from environment or defaults
cors_origins = _get_cors_origins()
logger.info(f"CORS origins configured: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register routers
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(extraction.router, prefix="/api/v1/extraction", tags=["extraction"])


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "core-cartographer-api"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Core Cartographer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
