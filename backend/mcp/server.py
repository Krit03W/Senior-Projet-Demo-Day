"""FastMCP server — registers all tools (DB + simulated) under one server."""
from __future__ import annotations

import json
from typing import Any, Dict

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from mcp.tools.database import query_database, get_schema
from mcp.tools.email import send_summary_email
from mcp.tools.slack import notify_slack_channel
from mcp.tools.report import generate_report

load_dotenv()

server = FastMCP("crm-copilot-mcp")


@server.tool()
async def mcp_query_database(sql: str) -> str:
    result = query_database(sql)
    return json.dumps(result, ensure_ascii=False, default=str)


@server.tool()
async def mcp_get_schema() -> str:
    result = get_schema()
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def mcp_send_summary_email(to: str, subject: str, body: str) -> str:
    result = send_summary_email(to, subject, body)
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def mcp_notify_slack_channel(channel: str, message: str) -> str:
    result = notify_slack_channel(channel, message)
    return json.dumps(result, ensure_ascii=False)


@server.tool()
async def mcp_generate_report(title: str, data_summary: str, format: str = "pdf") -> str:
    result = generate_report(title, data_summary, format)
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    print("Starting MCP server 'crm-copilot-mcp' (stdio transport).")
    print("Tools: mcp_query_database, mcp_get_schema, mcp_send_summary_email, "
          "mcp_notify_slack_channel, mcp_generate_report")
    server.run()
