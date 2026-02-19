/* ── Types shared across the frontend ─────────────────────────── */

export interface StepEvent {
  step_name: string;
  status: "pending" | "processing" | "success" | "failed" | "retry" | "skipped";
  detail: string;
  data: Record<string, unknown>;
}

export interface ToolResult {
  tool: string;
  result: {
    success: boolean;
    error?: string;
    sql?: string;
    columns?: string[];
    rows?: Record<string, unknown>[];
    row_count?: number;
    simulated?: boolean;
    note?: string;
    [key: string]: unknown;
  };
}

export interface ChatResult {
  session_id: string;
  agent_response: string;
  sql_used: string;
  intent: string;
  events: StepEvent[];
  tool_results: ToolResult[];
  had_retry: boolean;
}

export interface Scenario {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  prompt: string;
  difficulty: string;
  estimated_time: string;
  highlights: string[];
}

export interface ValidationCheck {
  parameter: string;
  value: string;
  status: "passed" | "failed" | "warning";
  detail: string;
}

export interface ValidationResult {
  tool_name: string;
  valid: boolean;
  checks: ValidationCheck[];
  errors: string[];
}

export interface ChatMessage {
  role: "user" | "agent";
  content: string;
  timestamp?: number;
  result?: ChatResult;
}

// Pipeline step names in order
export const PIPELINE_STEPS = [
  "intent",
  "tool_selection",
  "schema_validation",
  "execution",
  "response",
] as const;

export type PipelineStepName = (typeof PIPELINE_STEPS)[number];

export const STEP_LABELS: Record<string, { icon: string; label: string }> = {
  intent: { icon: "🧠", label: "Intent Recognition" },
  tool_selection: { icon: "🔧", label: "Tool Selection" },
  schema_validation: { icon: "📋", label: "Schema Validation" },
  execution: { icon: "⚡", label: "Execution" },
  response: { icon: "📊", label: "Response Generation" },
  retry: { icon: "🔄", label: "Retry" },
};
