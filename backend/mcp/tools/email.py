"""Simulated MCP tool — send_summary_email.

Returns a mock success response so we can demo multi-tool orchestration
without actually sending emails.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

SEND_EMAIL_SCHEMA = {
    "name": "send_summary_email",
    "description": "Send a summary email to a specified recipient with CRM data highlights.",
    "parameters": {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": "Recipient email address.",
            },
            "subject": {
                "type": "string",
                "description": "Email subject line.",
            },
            "body": {
                "type": "string",
                "description": "Email body text.",
            },
        },
        "required": ["to", "subject", "body"],
    },
}


def send_summary_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """Simulated email send — always succeeds."""
    return {
        "success": True,
        "simulated": True,
        "message_id": f"sim-email-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "to": to,
        "subject": subject,
        "body_preview": body[:120] + ("…" if len(body) > 120 else ""),
        "note": "📧 Email simulated for demo purposes.",
    }
