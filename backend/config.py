"""Centralised configuration loaded from environment / .env."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = Path(os.getenv("CRM_DB_PATH", str(BASE_DIR / "data" / "crmarena_data.db")))

# ── LLM ────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Agent ──────────────────────────────────────────────────────────
MAX_ROWS = int(os.getenv("AGENT_MAX_ROWS", "50"))
MAX_RETRIES = int(os.getenv("AGENT_MAX_RETRIES", "2"))

# ── Session ────────────────────────────────────────────────────────
SESSION_TIMEOUT_SECONDS = int(os.getenv("SESSION_TIMEOUT", "300"))  # 5 min
MAX_SESSIONS = int(os.getenv("MAX_SESSIONS", "20"))

# ── Rate Limiting ──────────────────────────────────────────────────
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT", "10"))
