"use client";

import React from "react";
import { StepEvent, PIPELINE_STEPS, STEP_LABELS } from "@/types";

interface PipelineVisualizerProps {
  events: StepEvent[];
}

function getStepStatus(stepName: string, events: StepEvent[]): StepEvent | null {
  // Find the latest event for this step
  const matching = events.filter((e) => e.step_name === stepName);
  return matching.length > 0 ? matching[matching.length - 1] : null;
}

function getRetryEvents(events: StepEvent[]): StepEvent[] {
  return events.filter((e) => e.step_name === "retry");
}

const STATUS_CLASSES: Record<string, string> = {
  pending: "step-pending",
  processing: "step-processing",
  success: "step-success",
  failed: "step-failed",
  retry: "step-retry",
  skipped: "step-skipped",
};

const STATUS_ICONS: Record<string, string> = {
  pending: "○",
  processing: "◉",
  success: "✅",
  failed: "❌",
  retry: "🔄",
  skipped: "⊘",
};

export default function PipelineVisualizer({ events }: PipelineVisualizerProps) {
  const retries = getRetryEvents(events);

  return (
    <div className="pipeline-visualizer">
      <h3 className="panel-section-title">Agent Pipeline</h3>
      <div className="pipeline-steps">
        {PIPELINE_STEPS.map((stepName, idx) => {
          const event = getStepStatus(stepName, events);
          const status = event?.status || "pending";
          const label = STEP_LABELS[stepName];
          const isLast = idx === PIPELINE_STEPS.length - 1;

          return (
            <React.Fragment key={stepName}>
              <div className={`pipeline-step ${STATUS_CLASSES[status] || "step-pending"}`}>
                <div className="step-icon-wrapper">
                  <span className="step-emoji">{label?.icon || "○"}</span>
                  <span className="step-status-icon">{STATUS_ICONS[status]}</span>
                </div>
                <div className="step-info">
                  <div className="step-name">{label?.label || stepName}</div>
                  {event?.detail ? (
                    <div className="step-detail">{event.detail}</div>
                  ) : null}
                  {stepName === "tool_selection" && event?.data?.tools ? (
                    <div className="step-tools">
                      {(event.data.tools as Array<{name: string}>).map((t: {name: string}, i: number) => (
                        <span key={i} className="tool-name-tag">{t.name}</span>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>

              {/* Connector line */}
              {!isLast && (
                <div className={`pipeline-connector ${status === "success" ? "connector-done" : ""} ${status === "processing" ? "connector-active" : ""}`} />
              )}

              {/* Show retry indicator after validation if applicable */}
              {stepName === "schema_validation" && retries.length > 0 && (
                <>
                  <div className="pipeline-step step-retry">
                    <div className="step-icon-wrapper">
                      <span className="step-emoji">🔄</span>
                      <span className="step-status-icon">⟳</span>
                    </div>
                    <div className="step-info">
                      <div className="step-name">Auto-Retry</div>
                      <div className="step-detail">
                        {retries[retries.length - 1]?.detail || "Retrying with corrected parameters…"}
                      </div>
                    </div>
                  </div>
                  <div className="pipeline-connector connector-retry" />
                </>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
