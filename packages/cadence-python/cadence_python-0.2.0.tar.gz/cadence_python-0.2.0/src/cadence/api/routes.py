"""Cadence API Routes Aggregation Module.

This module serves as the central aggregation point for all Cadence framework API endpoints.
It provides a clean interface for registering routes and initializing the API container.

Key Components:
    - Router aggregation for all API endpoints
    - API initialization and container setup
    - Route registration and middleware configuration
    - Health check and system status endpoints

Example:
    >>> from cadence.api.routes import router, initialize_api
    >>>
    >>> # Initialize API container
    >>> await initialize_api(settings)
    >>>
    >>> # Include router in FastAPI app
    >>> app.include_router(router, prefix="/api/v1")
"""

from fastapi import APIRouter

from cadence.api.routers import chat, plugins, system
from cadence.config.settings import Settings

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
router.include_router(system.router, prefix="/system", tags=["system"])


# Root endpoint
@router.get("/")
async def root():
    """Root endpoint for the Cadence API."""
    return {"message": "Welcome to Cadence AI Framework API", "version": "1.0.0", "docs": "/docs", "health": "/health"}


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "cadence-api", "version": "1.0.0"}


async def initialize_api(settings: Settings) -> None:
    """Initialize the API container and dependencies."""
    # This function can be used to set up any API-level dependencies
    # such as database connections, external services, etc.
    pass
