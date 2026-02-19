"""Simulated MCP tool — generate_report.

Returns a mock report summary for demo purposes.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

GENERATE_REPORT_SCHEMA = {
    "name": "generate_report",
    "description": "Generate a summary report from CRM data results. Returns a formatted report object.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Report title.",
            },
            "data_summary": {
                "type": "string",
                "description": "A text summary of the data to include.",
            },
            "format": {
                "type": "string",
                "enum": ["pdf", "csv", "json"],
                "description": "Output format of the report.",
            },
        },
        "required": ["title", "data_summary"],
    },
}


def generate_report(
    title: str,
    data_summary: str,
    format: str = "pdf",
) -> Dict[str, Any]:
    """Simulated report generation — always succeeds."""
    return {
        "success": True,
        "simulated": True,
        "report_id": f"rpt-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "title": title,
        "format": format,
        "data_summary_preview": data_summary[:150] + ("…" if len(data_summary) > 150 else ""),
        "note": "📊 Report generation simulated for demo purposes.",
    }
