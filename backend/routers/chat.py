"""Chat router — WebSocket streaming + REST fallback."""
from __future__ import annotations

import asyncio
import json
import traceback
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from agent.graph import run_agent_pipeline
from session.manager import session_manager

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    agent_response: str
    sql_used: str
    intent: str
    events: list
    tool_results: list
    had_retry: bool


# ── REST endpoint (fallback) ──────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    session = session_manager.get_or_create(req.session_id)
    session.add_message("user", req.message)

    state = await run_agent_pipeline(
        user_message=req.message,
        session_id=session.session_id,
    )

    session.add_message("agent", state.agent_response)

    return ChatResponse(
        session_id=session.session_id,
        agent_response=state.agent_response,
        sql_used=state.sql_used,
        intent=state.intent,
        events=[e.to_dict() for e in state.events],
        tool_results=state.tool_results,
        had_retry=state.had_retry,
    )


# ── WebSocket for real-time streaming ─────────────────────────────

@router.websocket("/chat/stream")
async def chat_stream(ws: WebSocket):
    await ws.accept()

    try:
        while True:
            raw = await ws.receive_text()
            data = json.loads(raw)
            message = data.get("message", "")
            session_id = data.get("session_id")

            session = session_manager.get_or_create(session_id)
            session.add_message("user", message)

            # Send session ID immediately
            await ws.send_json({"type": "session", "session_id": session.session_id})

            async def on_event(event: Dict[str, Any]) -> None:
                await ws.send_json({"type": "event", **event})

            try:
                state = await run_agent_pipeline(
                    user_message=message,
                    session_id=session.session_id,
                    on_event=on_event,
                )

                session.add_message("agent", state.agent_response)

                await ws.send_json({
                    "type": "result",
                    "session_id": session.session_id,
                    "agent_response": state.agent_response,
                    "sql_used": state.sql_used,
                    "intent": state.intent,
                    "tool_results": state.tool_results,
                    "had_retry": state.had_retry,
                    "events": [e.to_dict() for e in state.events],
                })

            except Exception as exc:
                await ws.send_json({
                    "type": "error",
                    "error": str(exc),
                    "detail": traceback.format_exc(),
                })

    except WebSocketDisconnect:
        pass
