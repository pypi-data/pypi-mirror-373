"""Cadence Framework Domain Layer - Business Models and Core Logic.

This module contains the core business logic and domain models for the Cadence
multi-agent AI framework. The domain layer follows clean architecture principles
and implements the core business entities and operations.

Key Components:
    - Models: Core business entities (User, Thread, Conversation)
    - DTOs: Data transfer objects for API communication
    - Services: Business logic operations
    - Validators: Domain-specific validation rules

Example:
    >>> from cadence.domain.models import User, Thread, ConversationTurn
    >>> from cadence.domain.dtos import ChatRequest, ChatResponse
    >>>
    >>> # Create domain objects
    >>> user = User(id="user123", name="John Doe")
    >>> thread = Thread(id="thread456", user_id=user.id)
    >>>
    >>> # Process business logic
    >>> conversation = ConversationTurn(
    ...     thread_id=thread.id,
    ...     user_message="Hello, world!",
    ...     agent_response="Hi there!"
    ... )
"""

from cadence.domain.dtos import ChatRequest, ChatResponse, TokenUsage
from cadence.domain.models import Conversation, Thread, User

__all__ = ["User", "Thread", "Conversation", "ChatRequest", "ChatResponse", "TokenUsage"]
