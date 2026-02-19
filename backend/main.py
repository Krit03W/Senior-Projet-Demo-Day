"""Agentic CRM Copilot — FastAPI Backend Entry Point."""
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="Agentic CRM Copilot",
    description="AI Agent Demo — MCP + LangGraph for CRM Actions",
    version="1.0.0-demo",
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
from routers.chat import router as chat_router
from routers.session import router as session_router
from routers.scenarios import router as scenarios_router

app.include_router(chat_router)
app.include_router(session_router)
app.include_router(scenarios_router)


@app.get("/")
async def root():
    return {"message": "Agentic CRM Copilot API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
