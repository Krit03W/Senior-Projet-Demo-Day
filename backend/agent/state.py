"""Agent state definition for LangGraph."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StepEvent:
    """One step in the agent pipeline, streamed to the UI."""
    step_name: str          # intent | tool_selection | schema_validation | execution | response
    status: str             # pending | processing | success | failed | retry
    detail: str = ""        # human-readable 1-liner
    data: Optional[Dict[str, Any]] = None   # payload (tool result, validation, etc.)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_name": self.step_name,
            "status": self.status,
            "detail": self.detail,
            "data": self.data or {},
        }


@dataclass
class AgentState:
    """Accumulated state that flows through every LangGraph node."""
    user_message: str = ""
    session_id: str = ""

    # Populated by intent node
    intent: str = ""
    intent_detail: str = ""

    # Populated by tool selector
    selected_tools: List[Dict[str, Any]] = field(default_factory=list)
    # each: {"name": str, "arguments": dict}

    # Populated by validator
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    validation_passed: bool = False

    # Populated by executor
    tool_results: List[Dict[str, Any]] = field(default_factory=list)

    # Populated by responder
    agent_response: str = ""
    sql_used: str = ""

    # Error / retry tracking
    retry_count: int = 0
    max_retries: int = 2
    error_message: str = ""
    had_retry: bool = False

    # Events for UI streaming
    events: List[StepEvent] = field(default_factory=list)

    def add_event(self, step_name: str, status: str, detail: str = "", data: Any = None) -> None:
        self.events.append(StepEvent(step_name, status, detail, data))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_message": self.user_message,
            "intent": self.intent,
            "intent_detail": self.intent_detail,
            "selected_tools": self.selected_tools,
            "validation_results": self.validation_results,
            "validation_passed": self.validation_passed,
            "tool_results": self.tool_results,
            "agent_response": self.agent_response,
            "sql_used": self.sql_used,
            "retry_count": self.retry_count,
            "had_retry": self.had_retry,
            "error_message": self.error_message,
            "events": [e.to_dict() for e in self.events],
        }
