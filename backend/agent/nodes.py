"""LangGraph node implementations for the CRM Copilot agent.

Each node takes an AgentState, mutates it, and emits UI events.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from google import genai
from google.genai import types
from dotenv import load_dotenv

from agent.state import AgentState
from mcp.tools.database import query_database, get_schema, QUERY_DATABASE_SCHEMA, GET_SCHEMA_SCHEMA
from mcp.tools.email import send_summary_email
from mcp.tools.slack import notify_slack_channel
from mcp.tools.report import generate_report
from mcp.validator import validate_tool_call, TOOL_SCHEMAS
from config import GEMINI_API_KEY, GEMINI_MODEL, MAX_ROWS

load_dotenv()

# ── Gemini client singleton ───────────────────────────────────────

_client = None

def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _schema_doc() -> str:
    """Get a compact schema description for prompts."""
    result = get_schema()
    schema = result.get("schema", {})
    lines = []
    for table, cols in schema.items():
        lines.append(f"  - {table}: {', '.join(cols)}")
    return "\n".join(lines)


TOOL_DESCRIPTIONS = "\n".join(
    f"  - {name}: {s.get('description', '')}" for name, s in TOOL_SCHEMAS.items()
)

# ── Node 1: Intent Recognition ────────────────────────────────────

def intent_node(state: AgentState) -> AgentState:
    """Classify user intent and produce a brief description."""
    state.add_event("intent", "processing", "Analyzing user message…")

    prompt = f"""You are an intent classifier for a CRM copilot.
Given the user's message, respond with a JSON object:
{{
  "intent": "<one of: query_data, multi_step_action, report_request, unknown>",
  "detail": "<1-sentence description of what the user wants>",
  "needs_tools": ["<list of tool names that might be needed>"]
}}

Available tools:
{TOOL_DESCRIPTIONS}

Available CRM tables:
{_schema_doc()}

User message: {state.user_message}

Respond with JSON only."""

    client = _get_client()
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    try:
        payload = json.loads(resp.text)
    except json.JSONDecodeError:
        payload = {"intent": "query_data", "detail": state.user_message, "needs_tools": ["query_database"]}

    state.intent = payload.get("intent", "query_data")
    state.intent_detail = payload.get("detail", state.user_message)

    state.add_event("intent", "success", state.intent_detail, {
        "intent_type": state.intent,
        "suggested_tools": payload.get("needs_tools", []),
    })
    return state


# ── Node 2: Tool Selection ────────────────────────────────────────

def tool_selection_node(state: AgentState) -> AgentState:
    """Select tools and generate arguments based on user intent."""
    state.add_event("tool_selection", "processing", "Selecting tools and building parameters…")

    schema_doc = _schema_doc()

    prompt = f"""You are a CRM copilot tool planner. Based on the user's request,
select the appropriate tools and generate the correct arguments for each.

Respond with a JSON object:
{{
  "tool_calls": [
    {{
      "name": "<tool name>",
      "arguments": {{ ... }}
    }}
  ]
}}

Available tools and their schemas:
{json.dumps(TOOL_SCHEMAS, indent=2)}

Available CRM database tables:
{schema_doc}

SQL rules:
- Only SELECT statements
- Always include LIMIT {MAX_ROWS} if no limit specified
- Table names "Case" and "Order" must be double-quoted in SQL
- Use correct column names from the schema above

User intent: {state.intent_detail}
User message: {state.user_message}
{f'Previous error (retry #{state.retry_count}): {state.error_message}' if state.error_message else ''}

Respond with JSON only."""

    client = _get_client()
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )

    try:
        payload = json.loads(resp.text)
    except json.JSONDecodeError:
        state.add_event("tool_selection", "failed", "Could not parse tool selection response")
        state.selected_tools = []
        return state

    state.selected_tools = payload.get("tool_calls", [])

    tool_names = [t["name"] for t in state.selected_tools]
    state.add_event("tool_selection", "success", f"Selected: {', '.join(tool_names)}", {
        "tools": state.selected_tools,
    })
    return state


# ── Node 3: Schema Validation ─────────────────────────────────────

def validation_node(state: AgentState) -> AgentState:
    """Validate every tool call against MCP schemas."""
    state.add_event("schema_validation", "processing", "Validating parameters against MCP schemas…")

    all_valid = True
    results = []

    for tool_call in state.selected_tools:
        name = tool_call.get("name", "")
        args = tool_call.get("arguments", {})
        vr = validate_tool_call(name, args)
        results.append(vr.to_dict())
        if not vr.valid:
            all_valid = False

    state.validation_results = results
    state.validation_passed = all_valid

    if all_valid:
        state.add_event("schema_validation", "success", "All parameters valid ✓", {
            "validation": results,
        })
    else:
        errors = []
        for r in results:
            errors.extend(r.get("errors", []))
        state.add_event("schema_validation", "failed", f"Validation failed: {'; '.join(errors)}", {
            "validation": results,
        })
        state.error_message = "; ".join(errors)

    return state


# ── Node 4: Tool Execution ────────────────────────────────────────

TOOL_FUNCTIONS = {
    "query_database": lambda args: query_database(**args),
    "get_schema": lambda args: get_schema(),
    "send_summary_email": lambda args: send_summary_email(**args),
    "notify_slack_channel": lambda args: notify_slack_channel(**args),
    "generate_report": lambda args: generate_report(**args),
}


def execution_node(state: AgentState) -> AgentState:
    """Execute validated tool calls and collect results."""
    state.add_event("execution", "processing", "Executing tools…")
    state.tool_results = []

    for tool_call in state.selected_tools:
        name = tool_call.get("name", "")
        args = tool_call.get("arguments", {})
        fn = TOOL_FUNCTIONS.get(name)

        if fn is None:
            result = {"success": False, "error": f"No executor for tool '{name}'"}
        else:
            try:
                result = fn(args)
            except Exception as exc:
                result = {"success": False, "error": str(exc)}

        state.tool_results.append({"tool": name, "result": result})

        # Track SQL for display
        if name == "query_database" and isinstance(result, dict):
            state.sql_used = result.get("sql", args.get("sql", ""))

    all_ok = all(
        r.get("result", {}).get("success", False) for r in state.tool_results
    )

    if all_ok:
        state.add_event("execution", "success", f"Executed {len(state.tool_results)} tool(s) successfully", {
            "results": _safe_results(state.tool_results),
        })
    else:
        errs = [
            r["result"].get("error", "unknown")
            for r in state.tool_results
            if not r["result"].get("success", False)
        ]
        state.error_message = "; ".join(errs)
        state.add_event("execution", "failed", f"Execution error: {state.error_message}", {
            "results": _safe_results(state.tool_results),
        })

    return state


def _safe_results(results: List[Dict], max_rows: int = 10) -> List[Dict]:
    """Truncate large results for UI streaming."""
    safe = []
    for r in results:
        sr = dict(r)
        res = sr.get("result", {})
        if isinstance(res, dict) and "rows" in res:
            res = dict(res)
            if len(res["rows"]) > max_rows:
                res["rows"] = res["rows"][:max_rows]
                res["truncated"] = True
            sr["result"] = res
        safe.append(sr)
    return safe


# ── Node 5: Response Generation ───────────────────────────────────

def response_node(state: AgentState) -> AgentState:
    """Generate a natural-language reply summarising tool results."""
    state.add_event("response", "processing", "Generating response…")

    # Build a compact summary of all tool results
    result_summary = json.dumps(state.tool_results, ensure_ascii=False, default=str)
    if len(result_summary) > 3000:
        result_summary = result_summary[:3000] + "…(truncated)"

    prompt = f"""You are a CRM copilot. Summarise the tool execution results for the user.
Be concise (2-4 sentences). Use Thai language if the user asked in Thai, else English.
Do NOT expose internal implementation details.

User question: {state.user_message}
Tool results: {result_summary}
{f'Note: auto-recovered from error via retry.' if state.had_retry else ''}

Respond with plain text only (no JSON)."""

    client = _get_client()
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    state.agent_response = resp.text.strip()
    state.add_event("response", "success", "Response generated", {
        "response": state.agent_response,
    })
    return state
