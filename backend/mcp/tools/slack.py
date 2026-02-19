"""Simulated MCP tool — notify_slack_channel.

Returns a mock success response for demo purposes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

NOTIFY_SLACK_SCHEMA = {
    "name": "notify_slack_channel",
    "description": "Post a notification message to a Slack channel about CRM updates or alerts.",
    "parameters": {
        "type": "object",
        "properties": {
            "channel": {
                "type": "string",
                "description": "Slack channel name (e.g. #sales-alerts).",
            },
            "message": {
                "type": "string",
                "description": "Message content to post.",
            },
        },
        "required": ["channel", "message"],
    },
}


def notify_slack_channel(channel: str, message: str) -> Dict[str, Any]:
    """Simulated Slack notification — always succeeds."""
    return {
        "success": True,
        "simulated": True,
        "ts": datetime.now(timezone.utc).isoformat(),
        "channel": channel,
        "message_preview": message[:100] + ("…" if len(message) > 100 else ""),
        "note": "💬 Slack notification simulated for demo purposes.",
    }
