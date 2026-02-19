"""Session router — reset & status."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from session.manager import session_manager

router = APIRouter(prefix="/api/session", tags=["session"])


class ResetRequest(BaseModel):
    session_id: str


class ResetResponse(BaseModel):
    success: bool
    session_id: str


@router.post("/reset", response_model=ResetResponse)
async def reset_session(req: ResetRequest) -> ResetResponse:
    ok = session_manager.reset_session(req.session_id)
    return ResetResponse(success=ok, session_id=req.session_id)
