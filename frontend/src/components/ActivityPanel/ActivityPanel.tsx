"use client";

import React from "react";
import { StepEvent } from "@/types";
import PipelineVisualizer from "./PipelineVisualizer";
import MCPValidationCard from "./MCPValidationCard";

interface ActivityPanelProps {
  events: StepEvent[];
  loading: boolean;
}

export default function ActivityPanel({ events, loading }: ActivityPanelProps) {
  return (
    <div className="activity-panel">
      <div className="panel-header">
        <h2>🧠 Agent Activity</h2>
        {loading && <span className="panel-loading">Processing…</span>}
      </div>

      {events.length === 0 ? (
        <div className="activity-empty">
          <div className="activity-empty-icon">⚙️</div>
          <p>เมื่อ Agent เริ่มทำงาน จะแสดง Pipeline Steps ที่นี่</p>
          <div className="activity-empty-steps">
            <span>🧠 Intent</span>
            <span>→</span>
            <span>🔧 Tool Selection</span>
            <span>→</span>
            <span>📋 Validation</span>
            <span>→</span>
            <span>⚡ Execute</span>
            <span>→</span>
            <span>📊 Response</span>
          </div>
        </div>
      ) : (
        <>
          <PipelineVisualizer events={events} />
          <MCPValidationCard events={events} />

          {/* Event log */}
          <div className="event-log">
            <h3 className="panel-section-title">📜 Activity Log</h3>
            <div className="event-log-list">
              {events.map((ev, i) => (
                <div key={i} className={`log-entry log-${ev.status}`}>
                  <span className="log-step">{ev.step_name}</span>
                  <span className="log-status">{ev.status}</span>
                  <span className="log-detail">{ev.detail}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
