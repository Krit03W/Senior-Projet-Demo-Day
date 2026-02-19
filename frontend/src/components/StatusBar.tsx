"use client";

import React from "react";

interface StatusBarProps {
  connected: boolean;
  dbTables: number;
  responseTime: number | null;
  sessionId: string | null;
}

export default function StatusBar({ connected, dbTables, responseTime, sessionId }: StatusBarProps) {
  return (
    <footer className="status-bar">
      <div className="status-item">
        <span className={`status-light ${connected ? "light-green" : "light-red"}`} />
        MCP Server: {connected ? "Connected" : "Disconnected"}
      </div>
      <div className="status-item">
        🗄️ DB: CRM Arena ({dbTables} tables)
      </div>
      {responseTime !== null && (
        <div className="status-item">
          ⏱️ {responseTime.toFixed(1)}s
        </div>
      )}
      {sessionId && (
        <div className="status-item session-id">
          🔑 {sessionId}
        </div>
      )}
    </footer>
  );
}
