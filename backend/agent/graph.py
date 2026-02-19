"""LangGraph state machine for the CRM Copilot agent.

Graph:  intent → tool_selection → validation → [retry?] → execution → response
"""
from __future__ import annotations

from typing import Any, Dict

from agent.state import AgentState
from agent.nodes import (
    intent_node,
    tool_selection_node,
    validation_node,
    execution_node,
    response_node,
)


def _should_retry(state: AgentState) -> bool:
    """After validation or execution failure, decide if we should retry."""
    if state.validation_passed and all(
        r.get("result", {}).get("success", False)
        for r in state.tool_results
    ):
        return False
    return state.retry_count < state.max_retries


async def run_agent_pipeline(user_message: str, session_id: str = "", on_event=None):
    """Execute the full agent pipeline, emitting events for each step.

    Parameters
    ----------
    user_message : str
        Natural-language input from the user.
    session_id : str
        Used for logging/tracking.
    on_event : callable | None
        ``async def on_event(event_dict)`` — called after every step.

    Returns
    -------
    AgentState
        The completed state with all results & events.
    """
    state = AgentState(user_message=user_message, session_id=session_id)

    async def emit() -> None:
        if on_event and state.events:
            await on_event(state.events[-1].to_dict())

    # Step 1: Intent recognition
    state = intent_node(state)
    await emit()

    # Retry loop covers tool_selection → validation → execution
    while True:
        # Step 2: Tool selection
        state = tool_selection_node(state)
        await emit()

        if not state.selected_tools:
            # No tools → just generate a direct response
            state.add_event("schema_validation", "skipped", "No tools selected")
            await emit()
            state.add_event("execution", "skipped", "No tools to execute")
            await emit()
            break

        # Step 3: Schema validation
        state = validation_node(state)
        await emit()

        if not state.validation_passed:
            if _should_retry(state):
                state.retry_count += 1
                state.had_retry = True
                state.add_event("retry", "processing",
                                f"Retrying (attempt {state.retry_count}/{state.max_retries})…",
                                {"reason": state.error_message})
                await emit()
                continue
            else:
                # Give up → still generate a (failed) response
                state.add_event("execution", "skipped", "Skipped due to validation failure")
                await emit()
                break

        # Step 4: Execution
        state = execution_node(state)
        await emit()

        exec_ok = all(
            r.get("result", {}).get("success", False) for r in state.tool_results
        )
        if not exec_ok and _should_retry(state):
            state.retry_count += 1
            state.had_retry = True
            state.add_event("retry", "processing",
                            f"Retrying (attempt {state.retry_count}/{state.max_retries})…",
                            {"reason": state.error_message})
            await emit()
            continue

        # All good (or exhausted retries)
        break

    # Step 5: Response generation
    state = response_node(state)
    await emit()

    return state
