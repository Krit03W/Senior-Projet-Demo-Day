"use client";

import React from "react";
import { Scenario } from "@/types";

interface ScenarioCardsProps {
  scenarios: Scenario[];
  onSelect: (prompt: string) => void;
  disabled: boolean;
}

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "#22c55e",
  medium: "#f59e0b",
  advanced: "#ef4444",
};

export default function ScenarioCards({ scenarios, onSelect, disabled }: ScenarioCardsProps) {
  return (
    <div className="scenario-cards">
      {scenarios.map((s) => (
        <button
          key={s.id}
          className="scenario-card"
          onClick={() => onSelect(s.prompt)}
          disabled={disabled}
        >
          <div className="scenario-header">
            <span className="scenario-title">{s.title}</span>
            <span
              className="difficulty-badge"
              style={{ backgroundColor: DIFFICULTY_COLORS[s.difficulty] || "#888" }}
            >
              {s.difficulty}
            </span>
          </div>
          <p className="scenario-subtitle">{s.subtitle}</p>
          <div className="scenario-highlights">
            {s.highlights.map((h, i) => (
              <span key={i} className="highlight-tag">{h}</span>
            ))}
          </div>
          <span className="scenario-time">{s.estimated_time}</span>
        </button>
      ))}
    </div>
  );
}
