"""Cadence Multi-Agent AI Framework Application Entry Point.

This module provides the main application factory for the Cadence framework, which is a
plugin-based multi-agent conversational AI system built on FastAPI.

Key Components:
    CadenceApplication: Main application factory that configures and runs the FastAPI server
    with complete lifecycle management including startup, shutdown, and health checks.

Basic usage to run the Cadence application:
    >>> from cadence.main import CadenceApplication
    >>> from cadence.config.settings import Settings
    >>>
    >>> settings = Settings()
    >>> app = CadenceApplication(settings)
    >>> app.run()

For running as a module:
    >>> from cadence.main import app
    >>> # app is ready to use with uvicorn
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from cadence.config.settings import Settings
from cadence.core.services.service_container import ServiceContainer

# Global application instance for module-level access
app_instance: Optional[FastAPI] = None


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    cadence_app = CadenceApplication()
    return cadence_app.create_app()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next):
        # Log request
        logging.info(f"Request: {request.method} {request.url}")

        # Process request
        response = await call_next(request)

        # Log response
        logging.info(f"Response: {response.status_code}")

        return response


class CadenceApplication:
    """Cadence FastAPI application factory with complete lifecycle management.

    This class orchestrates the creation, configuration, and execution of the Cadence
    multi-agent AI framework, providing a clean interface for both development and
    production deployment.
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize the Cadence application with configuration and logging.

        Args:
            settings: Configuration settings. If None, loads from environment.
        """
        self.settings = settings or Settings()
        self.logger = self._setup_logging()
        self.app: Optional[FastAPI] = None
        self.service_container: Optional[ServiceContainer] = None

    def _setup_logging(self) -> logging.Logger:
        """Set up a consistent log format across all Cadence components with
        appropriate log levels based on configuration.
        """
        logging.basicConfig(
            level=logging.DEBUG if self.settings.debug else logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("cadence.log") if self.settings.debug else logging.NullHandler(),
            ],
        )
        return logging.getLogger(__name__)

    async def _startup(self):
        """Initialize services and dependencies on application startup."""
        try:
            self.logger.info("Starting Cadence 🤖 Multi-agents AI Framework...")

            # Initialize service container
            self.service_container = ServiceContainer()
            await self.service_container.initialize(self.settings)

            self.logger.info("Cadence 🤖 Multi-agents AI Framework started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start Cadence: {e}")
            raise

    async def _shutdown(self):
        """Clean up resources on application shutdown."""
        try:
            self.logger.info("Shutting down Cadence 🤖 Multi-agents AI Framework...")

            if self.service_container:
                await self.service_container.cleanup()

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application with all middleware and routes."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await self._startup()
            yield
            await self._shutdown()

        self.app = FastAPI(
            title="Cadence 🤖 Multi-agents AI Framework",
            description="A plugin-based multi-agent conversational AI framework",
            version="1.0.0",
            lifespan=lifespan,
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add request logging middleware
        self.app.add_middleware(RequestLoggingMiddleware)

        # Add health check endpoint
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "message": "Cadence 🤖 Multi-agents AI Framework", "version": "1.0.0"}

        # Add root endpoint
        @self.app.get("/")
        async def root():
            return {"message": "Welcome to Cadence 🤖 Multi-agents AI Framework", "version": "1.0.0", "docs": "/docs"}

        return self.app

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the Cadence server using Uvicorn with environment-appropriate configuration.

        Args:
            host: Host to bind to
            port: Port to bind to
        """
        app = self.create_app()

        # Configure uvicorn settings
        uvicorn_config = {
            "app": app,
            "host": host,
            "port": port,
            "reload": self.settings.debug,
            "log_level": "debug" if self.settings.debug else "info",
        }

        # Start the server
        uvicorn.run(**uvicorn_config)


# Module-level convenience functions
def get_app() -> FastAPI:
    """Get the configured FastAPI application instance."""
    return create_app()


# Main entry point for running as a module
if __name__ == "__main__":
    """Main entry point for running Cadence as a standalone application.

    This allows the application to be run directly with `python -m cadence` or by
    running the module directly with `python -m cadence`.
    """
    cadence_application = CadenceApplication()
    cadence_application.run()
