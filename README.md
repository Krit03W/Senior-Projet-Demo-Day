# 🚀 Agentic CRM Copilot — Demo MVP

> AI Agent ที่ทำงาน CRM จริง ผ่าน Model Context Protocol (MCP) + LangGraph

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# แก้ GEMINI_API_KEY ใน .env

# Run
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

เปิด http://localhost:3000

### 3. ใช้งาน Demo

1. เลือก 1 ใน 3 Scenario Cards หรือพิมพ์คำถาม CRM
2. ดู Agent Pipeline ทำงานแบบ real-time ที่ Activity Panel ด้านขวา
3. กด **Reset Demo** เพื่อเริ่มใหม่

## Architecture

```
Frontend (Next.js) ←→ WebSocket ←→ Backend (FastAPI)
                                      ├── LangGraph Agent Pipeline
                                      │   ├── Intent Recognition
                                      │   ├── Tool Selection
                                      │   ├── Schema Validation (MCP)
                                      │   ├── Execution
                                      │   └── Response Generation
                                      ├── MCP Tools
                                      │   ├── query_database (real)
                                      │   ├── get_schema (real)
                                      │   ├── send_summary_email (simulated)
                                      │   ├── notify_slack (simulated)
                                      │   └── generate_report (simulated)
                                      └── CRM Arena SQLite DB
```

## Demo Scenarios

| #   | Scenario          | Goal                              |
| --- | ----------------- | --------------------------------- |
| 1   | 📊 Simple Query   | Agent แปลงภาษาธรรมชาติ → SQL      |
| 2   | 📋 Multi-Step     | Agent ใช้หลาย tools ร่วมกัน       |
| 3   | ⚠️ Error Recovery | MCP จับ schema error → auto retry |
