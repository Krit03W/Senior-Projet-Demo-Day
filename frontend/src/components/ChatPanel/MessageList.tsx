"use client";

import React, { useRef, useEffect } from "react";
import { ChatMessage } from "@/types";

interface MessageListProps {
  messages: ChatMessage[];
}

export default function MessageList({ messages }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="empty-chat">
        <div className="empty-icon">🤖</div>
        <p>เลือก Scenario หรือพิมพ์คำถาม CRM เพื่อเริ่มต้น</p>
        <p className="empty-hint">ตัวอย่าง: &quot;แสดง 5 เคสล่าสุดที่มีสถานะ Escalated&quot;</p>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.role}`}>
          <div className="message-avatar">
            {msg.role === "user" ? "👤" : "🤖"}
          </div>
          <div className="message-content">
            <div className="message-role">
              {msg.role === "user" ? "You" : "CRM Copilot"}
            </div>
            <div className="message-text">{msg.content}</div>

            {/* SQL Preview */}
            {msg.result?.sql_used && (
              <div className="sql-preview">
                <div className="sql-label">SQL Generated</div>
                <code>{msg.result.sql_used}</code>
              </div>
            )}

            {/* Data Table */}
            {msg.result?.tool_results?.map((tr, j) => {
              const res = tr.result;
              if (!res?.rows || res.rows.length === 0) return null;
              return (
                <div key={j} className="result-table-wrapper">
                  <div className="result-table-header">
                    <span>📊 {res.row_count ?? res.rows.length} rows</span>
                    {res.simulated && <span className="sim-badge">Simulated</span>}
                  </div>
                  <div className="table-scroll">
                    <table className="result-table">
                      <thead>
                        <tr>
                          {res.columns?.map((col, ci) => (
                            <th key={ci}>{String(col)}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {res.rows.slice(0, 10).map((row, ri) => (
                          <tr key={ri}>
                            {res.columns?.map((col, ci) => (
                              <td key={ci}>{String((row as Record<string, unknown>)[String(col)] ?? "")}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              );
            })}

            {/* Retry badge */}
            {msg.result?.had_retry && (
              <div className="retry-badge-msg">🔄 Auto-recovered from schema mismatch</div>
            )}
          </div>
        </div>
      ))}
      <div ref={endRef} />
    </div>
  );
}
