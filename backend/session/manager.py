"""In-memory session manager for the demo."""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from config import SESSION_TIMEOUT_SECONDS, MAX_SESSIONS


class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = time.time()
        self.last_active = time.time()
        self.messages: List[Dict[str, str]] = []  # {"role": "user"/"agent", "content": "..."}

    def touch(self) -> None:
        self.last_active = time.time()

    def is_expired(self) -> bool:
        return (time.time() - self.last_active) > SESSION_TIMEOUT_SECONDS

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content, "timestamp": time.time()})
        self.touch()

    def reset(self) -> None:
        self.messages.clear()
        self.touch()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "last_active": self.last_active,
        }


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    def create(self) -> Session:
        self._evict_expired()
        if len(self._sessions) >= MAX_SESSIONS:
            self._evict_oldest()
        sid = uuid.uuid4().hex[:12]
        sess = Session(sid)
        self._sessions[sid] = sess
        return sess

    def get(self, session_id: str) -> Optional[Session]:
        sess = self._sessions.get(session_id)
        if sess and sess.is_expired():
            del self._sessions[session_id]
            return None
        if sess:
            sess.touch()
        return sess

    def get_or_create(self, session_id: str | None) -> Session:
        if session_id:
            s = self.get(session_id)
            if s:
                return s
        return self.create()

    def reset_session(self, session_id: str) -> bool:
        sess = self._sessions.get(session_id)
        if sess:
            sess.reset()
            return True
        return False

    def _evict_expired(self) -> None:
        expired = [k for k, v in self._sessions.items() if v.is_expired()]
        for k in expired:
            del self._sessions[k]

    def _evict_oldest(self) -> None:
        if not self._sessions:
            return
        oldest = min(self._sessions, key=lambda k: self._sessions[k].last_active)
        del self._sessions[oldest]


# ── Global singleton ──────────────────────────────────────────────
session_manager = SessionManager()
