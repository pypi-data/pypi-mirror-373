"""Cadence Framework Agent State Management - Multi-Agent Conversation State.

This module defines the comprehensive state management system for Cadence's multi-agent
conversation orchestration. It provides the data structures and state management
capabilities needed to track conversation flow, agent interactions, and system state.

Key Components:
    - AgentState: Core state container for agent conversations
    - StateManager: State persistence and retrieval operations
    - StateValidation: State integrity and validation rules
    - StateTransitions: State change management and history

State Management Features:
    - Conversation context preservation
    - Agent interaction tracking
    - Tool usage monitoring
    - Cost and token tracking
    - Session lifecycle management

Example:
    >>> from cadence.core.orchestrator.state import AgentState
    >>>
    >>> # Create agent state
    >>> state = AgentState(
    ...     thread_id="thread123",
    ...     user_id="user456",
    ...     current_agent="math_agent",
    ...     conversation_history=["Hello", "Hi there!"]
    ... )
    >>>
    >>> # Update state
    >>> state.add_message("user", "Calculate 2+2")
    >>> state.switch_agent("calculator_agent")
    >>>
    >>> # Get state summary
    >>> summary = state.get_summary()
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Complete state representation for Cadence's multi-agent conversations.

    This TypedDict defines the complete state structure for Cadence's multi-agent
    orchestration system, including conversation context, agent routing, and
    system metadata.
    """

    # Core identifiers
    thread_id: str = Field(..., description="Unique thread identifier")
    user_id: str = Field(..., description="User identifier")
    org_id: Optional[str] = Field(None, description="Organization identifier")

    # Agent routing
    current_agent: str = Field(..., description="Currently active agent")
    agent_history: List[str] = Field(default_factory=list, description="Agent interaction history")
    max_agent_hops: int = Field(default=25, description="Maximum agent switches allowed")

    # Conversation state
    conversation_history: List[str] = Field(default_factory=list, description="Message history")
    current_context: Optional[str] = Field(None, description="Current conversation context")

    # Tool usage
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool execution history")
    max_tool_hops: int = Field(default=50, description="Maximum tool calls allowed")

    # System metadata
    session_start: Optional[str] = Field(None, description="Session start timestamp")
    last_activity: Optional[str] = Field(None, description="Last activity timestamp")
    total_tokens: int = Field(default=0, description="Total tokens used")
    estimated_cost: float = Field(default=0.0, description="Estimated cost in USD")

    # Configuration
    settings: Dict[str, Any] = Field(default_factory=dict, description="Agent-specific settings")

    def add_message(self, sender: str, message: str) -> None:
        """Add a message to the conversation history."""
        self.conversation_history.append(f"{sender}: {message}")
        self.last_activity = "now"  # In real implementation, use actual timestamp

    def switch_agent(self, agent_name: str) -> bool:
        """Switch to a different agent if within hop limits."""
        if len(self.agent_history) >= self.max_agent_hops:
            return False

        self.agent_history.append(self.current_agent)
        self.current_agent = agent_name
        return True

    def add_tool_call(self, tool_name: str, result: Any) -> None:
        """Record a tool call and its result."""
        self.tool_calls.append(
            {
                "tool": tool_name,
                "result": str(result),
                "timestamp": "now",  # In real implementation, use actual timestamp
            }
        )

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        return {
            "thread_id": self.thread_id,
            "current_agent": self.current_agent,
            "message_count": len(self.conversation_history),
            "agent_hops": len(self.agent_history),
            "tool_calls": len(self.tool_calls),
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
        }

    def is_valid(self) -> bool:
        """Check if the current state is valid."""
        return (
            len(self.agent_history) <= self.max_agent_hops
            and len(self.tool_calls) <= self.max_tool_hops
            and bool(self.thread_id)
            and bool(self.user_id)
        )


# Convenience functions
def create_initial_state(thread_id: str, user_id: str, initial_agent: str = "default") -> AgentState:
    """Create a new agent state for a conversation."""
    return AgentState(
        thread_id=thread_id,
        user_id=user_id,
        current_agent=initial_agent,
        session_start="now",  # In real implementation, use actual timestamp
    )


def validate_state_transition(current_state: AgentState, new_agent: str) -> bool:
    """Validate if a state transition is allowed."""
    return current_state.switch_agent(new_agent)
