"""MCP Schema Validator — verifies tool parameters match their JSON schema
before execution and produces detailed validation reports for the UI."""
from __future__ import annotations

from typing import Any, Dict, List

from mcp.tools.database import QUERY_DATABASE_SCHEMA, GET_SCHEMA_SCHEMA
from mcp.tools.email import SEND_EMAIL_SCHEMA
from mcp.tools.slack import NOTIFY_SLACK_SCHEMA
from mcp.tools.report import GENERATE_REPORT_SCHEMA

# ── Tool registry ─────────────────────────────────────────────────

TOOL_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "query_database": QUERY_DATABASE_SCHEMA,
    "get_schema": GET_SCHEMA_SCHEMA,
    "send_summary_email": SEND_EMAIL_SCHEMA,
    "notify_slack_channel": NOTIFY_SLACK_SCHEMA,
    "generate_report": GENERATE_REPORT_SCHEMA,
}


def _check_type(value: Any, expected: str) -> bool:
    """Basic JSON-schema type check."""
    mapping = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    py_type = mapping.get(expected)
    if py_type is None:
        return True  # unknown type → pass
    return isinstance(value, py_type)


# ── Public API ────────────────────────────────────────────────────

class ValidationResult:
    """Structured result of a schema validation check."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.valid = True
        self.checks: List[Dict[str, Any]] = []
        self.errors: List[str] = []

    def add_check(self, param: str, value: Any, status: str, detail: str = "") -> None:
        self.checks.append(
            {"parameter": param, "value": _safe_repr(value), "status": status, "detail": detail}
        )
        if status == "failed":
            self.valid = False
            self.errors.append(detail or f"Validation failed for '{param}'")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "valid": self.valid,
            "checks": self.checks,
            "errors": self.errors,
        }


def _safe_repr(v: Any, maxlen: int = 80) -> str:
    s = repr(v)
    return s[:maxlen] + "…" if len(s) > maxlen else s


def validate_tool_call(tool_name: str, arguments: Dict[str, Any]) -> ValidationResult:
    """Validate *arguments* against the registered schema for *tool_name*.

    Returns a :class:`ValidationResult` with per-parameter checks.
    """
    result = ValidationResult(tool_name)

    schema = TOOL_SCHEMAS.get(tool_name)
    if schema is None:
        result.add_check("tool", tool_name, "failed", f"Unknown tool: '{tool_name}'")
        return result

    params_schema = schema.get("parameters", {})
    properties = params_schema.get("properties", {})
    required = params_schema.get("required", [])

    # Check required params are present
    for req in required:
        if req not in arguments:
            result.add_check(req, None, "failed", f"Missing required parameter: '{req}'")
        else:
            val = arguments[req]
            prop = properties.get(req, {})
            expected_type = prop.get("type")

            # enum check
            allowed = prop.get("enum")
            if allowed and val not in allowed:
                result.add_check(
                    req,
                    val,
                    "failed",
                    f"Value '{val}' not in allowed values: {allowed}",
                )
                continue

            # type check
            if expected_type and not _check_type(val, expected_type):
                result.add_check(
                    req,
                    val,
                    "failed",
                    f"Expected type '{expected_type}', got '{type(val).__name__}'",
                )
            else:
                result.add_check(req, val, "passed")

    # Check optional params that were provided
    for key, val in arguments.items():
        if key in required:
            continue  # already checked
        if key not in properties:
            result.add_check(key, val, "warning", f"Unknown parameter: '{key}' (will be ignored)")
        else:
            prop = properties[key]
            expected_type = prop.get("type")
            allowed = prop.get("enum")
            if allowed and val not in allowed:
                result.add_check(
                    key, val, "failed", f"Value '{val}' not in allowed: {allowed}"
                )
            elif expected_type and not _check_type(val, expected_type):
                result.add_check(
                    key, val, "failed", f"Expected '{expected_type}', got '{type(val).__name__}'"
                )
            else:
                result.add_check(key, val, "passed")

    return result
