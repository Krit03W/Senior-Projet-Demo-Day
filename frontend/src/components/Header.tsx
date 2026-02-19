"use client";

import React from "react";

interface HeaderProps {
  connected: boolean;
  toolCount: number;
  onReset: () => void;
}

export default function Header({ connected, toolCount, onReset }: HeaderProps) {
  return (
    <header className="app-header">
      <div className="header-left">
        <span className="logo">⚡</span>
        <h1 className="app-title">Agentic CRM Copilot</h1>
        <span className="app-subtitle">MCP + LangGraph Demo</span>
      </div>
      <div className="header-right">
        <div className={`status-badge ${connected ? "connected" : "disconnected"}`}>
          <span className="status-dot" />
          {connected ? "Connected" : "Disconnected"}
        </div>
        <div className="tool-badge">
          🔧 MCP Tools: {toolCount}
        </div>
        <button className="reset-btn" onClick={onReset}>
          ↻ Reset Demo
        </button>
      </div>
    </header>
  );
}
