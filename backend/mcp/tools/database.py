"""MCP Database tools — query_database & get_schema.

These are the *real* tools that hit the CRM Arena SQLite database.
"""
from __future__ import annotations

import re
import sqlite3
from typing import Any, Dict, List

from config import DB_PATH, MAX_ROWS


def _get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def _enforce_select(sql: str) -> None:
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")


def _ensure_limit(sql: str, limit: int = MAX_ROWS) -> str:
    if "limit" in sql.lower():
        return sql
    return f"{sql.rstrip().rstrip(';')} LIMIT {limit}"


def _quote_reserved(sql: str) -> str:
    """Double-quote reserved table names (Case, Order)."""
    for word in ("Case", "Order"):
        pattern = rf'(?<!")\b{re.escape(word)}\b(?!")'
        sql = re.sub(pattern, f'"{word}"', sql)
    return sql


# ── MCP Tool: query_database ──────────────────────────────────────

QUERY_DATABASE_SCHEMA = {
    "name": "query_database",
    "description": "Execute a read-only SQL SELECT query on the CRM database and return results.",
    "parameters": {
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "A valid SQLite SELECT statement.",
            }
        },
        "required": ["sql"],
    },
}


def query_database(sql: str) -> Dict[str, Any]:
    """Execute a SELECT query; return columns + rows."""
    _enforce_select(sql)
    sql = _ensure_limit(sql)
    sql = _quote_reserved(sql)

    try:
        with _get_conn() as conn:
            cursor = conn.execute(sql)
            columns = [d[0] for d in cursor.description]
            rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {"success": True, "sql": sql, "columns": columns, "rows": rows, "row_count": len(rows)}
    except sqlite3.Error as exc:
        return {"success": False, "error": str(exc), "sql": sql}


# ── MCP Tool: get_schema ──────────────────────────────────────────

GET_SCHEMA_SCHEMA = {
    "name": "get_schema",
    "description": "Return available CRM database tables and their columns for query grounding.",
    "parameters": {
        "type": "object",
        "properties": {},
    },
}


def get_schema() -> Dict[str, Any]:
    """Return mapping: table -> [column_names]."""
    schema: Dict[str, List[str]] = {}
    with _get_conn() as conn:
        tables = [
            r[0]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        ]
        for table in tables:
            cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')]
            schema[table] = cols
    return {"success": True, "schema": schema}
