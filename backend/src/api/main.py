"""
Main FastAPI application with CORS, lifecycle management, and route configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .routes import files, analysis, extraction
from ..cache.file_cache import file_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown tasks including cache cleanup.
    """
    # Startup: clean expired cache
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

# CORS configuration
# Note: Different URLs for browser vs container access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Development: Browser requests
        "http://frontend:3000",       # Docker: Container hostname (not typically needed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
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
