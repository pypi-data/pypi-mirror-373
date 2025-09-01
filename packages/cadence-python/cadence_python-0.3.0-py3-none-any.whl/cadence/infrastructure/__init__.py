"""Cadence Framework Infrastructure Layer - External Services and Data Persistence.

This module provides the infrastructure layer implementation for the Cadence
multi-agent AI framework. It implements the infrastructure concerns including
database connections, external service integrations, and plugin management.

Key Components:
    - Database: Multi-backend database connections and repositories
    - LLM: Language model provider integrations
    - Plugins: Plugin discovery and management system
    - External Services: Third-party API integrations

Example:
    >>> from cadence.infrastructure.database import DatabaseFactory
    >>> from cadence.config import Settings
    >>>
    >>> # Initialize database connections
    >>> settings = Settings()
    >>> db_factory = DatabaseFactory(settings)
    >>>
    >>> # Get database connection
    >>> db = await db_factory.get_database("postgresql")
    >>>
    >>> # Initialize LLM factory
    >>> from cadence.infrastructure.llm import LLMModelFactory
    >>> llm_factory = LLMModelFactory(settings)
    >>>
    >>> # Get LLM provider
    >>> llm = await llm_factory.get_provider("openai")
"""

from cadence.infrastructure.database import DatabaseFactory
from cadence.infrastructure.llm import LLMModelFactory
from cadence.infrastructure.plugins import SDKPluginManager

__all__ = ["DatabaseFactory", "LLMModelFactory", "SDKPluginManager"]
