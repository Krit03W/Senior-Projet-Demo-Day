"""Scenarios router — preset demo scenarios."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["scenarios"])

SCENARIOS: List[Dict[str, Any]] = [
    {
        "id": "simple_query",
        "title": "📊 Simple CRM Query",
        "subtitle": "ค้นหาข้อมูลจาก CRM ง่ายๆ",
        "description": "ถามข้อมูล CRM ด้วยภาษาธรรมชาติ → Agent แปลงเป็น SQL แล้วดึงใปข้อมูล",
        "prompt": "แสดง 5 เคสล่าสุดที่มีสถานะ Escalated",
        "difficulty": "easy",
        "estimated_time": "~10 seconds",
        "highlights": ["Intent Recognition", "SQL Generation", "Schema Validation"],
    },
    {
        "id": "multi_step",
        "title": "📋 Multi-Step Action",
        "subtitle": "Agent ทำงานหลายขั้นตอนอัตโนมัติ",
        "description": "Agent ค้นหาข้อมูล → สร้าง report → แจ้งเตือน Slack อัตโนมัติ",
        "prompt": "สรุปยอด order ของลูกค้า top 3 แล้วส่ง report ให้ทีม sales ทาง Slack",
        "difficulty": "medium",
        "estimated_time": "~20 seconds",
        "highlights": ["Multi-Tool Orchestration", "query_database → generate_report → notify_slack"],
    },
    {
        "id": "error_recovery",
        "title": "⚠️ Error Recovery",
        "subtitle": "MCP ช่วยจับ error + auto-retry",
        "description": "Agent ทำผิด → MCP จับได้ → Agent แก้ไขอัตโนมัติ แสดงพลัง validation",
        "prompt": "ดึงข้อมูลเคสของ agent_id 'USR-005' ที่สร้างในเดือนนี้",
        "difficulty": "advanced",
        "estimated_time": "~25 seconds",
        "highlights": ["Schema Mismatch Detection", "Auto-Recovery", "Retry Pipeline"],
    },
]


@router.get("/scenarios")
async def list_scenarios() -> List[Dict[str, Any]]:
    return SCENARIOS


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    from mcp.tools.database import get_schema
    try:
        schema = get_schema()
        table_count = len(schema.get("schema", {}))
        db_ok = True
    except Exception:
        table_count = 0
        db_ok = False

    return {
        "status": "healthy" if db_ok else "degraded",
        "database": {"connected": db_ok, "tables": table_count},
        "mcp_tools": 5,
        "version": "1.0.0-demo",
    }


@router.get("/schema")
async def get_db_schema() -> Dict[str, Any]:
    from mcp.tools.database import get_schema
    return get_schema()
