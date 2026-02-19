"use client";

import React from "react";
import { StepEvent, ValidationCheck } from "@/types";

interface MCPValidationCardProps {
  events: StepEvent[];
}

export default function MCPValidationCard({ events }: MCPValidationCardProps) {
  // Find the latest schema_validation event
  const validationEvent = [...events]
    .reverse()
    .find((e) => e.step_name === "schema_validation" && e.data?.validation);

  if (!validationEvent) return null;

  const validations = validationEvent.data.validation as Array<{
    tool_name: string;
    valid: boolean;
    checks: ValidationCheck[];
    errors: string[];
  }>;

  return (
    <div className="mcp-validation-card">
      <h3 className="panel-section-title">📋 MCP Schema Validation</h3>
      {validations.map((v, idx) => (
        <div key={idx} className={`validation-block ${v.valid ? "valid" : "invalid"}`}>
          <div className="validation-header">
            <span className="validation-tool">{v.tool_name}</span>
            <span className={`validation-badge ${v.valid ? "badge-pass" : "badge-fail"}`}>
              {v.valid ? "✅ Valid" : "❌ Failed"}
            </span>
          </div>
          <table className="validation-table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Value</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {v.checks.map((c, ci) => (
                <tr key={ci} className={`check-${c.status}`}>
                  <td className="param-name">{c.parameter}</td>
                  <td className="param-value">
                    <code>{String(c.value).slice(0, 60)}</code>
                  </td>
                  <td className="param-status">
                    {c.status === "passed" ? "✅" : c.status === "failed" ? "❌" : "⚠️"}
                    {c.detail && <span className="check-detail">{c.detail}</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {v.errors.length > 0 && (
            <div className="validation-errors">
              {v.errors.map((err, ei) => (
                <div key={ei} className="error-line">⚠ {err}</div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
