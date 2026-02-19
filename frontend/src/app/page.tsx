"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import Header from "@/components/Header";
import ChatPanel from "@/components/ChatPanel/ChatPanel";
import ActivityPanel from "@/components/ActivityPanel/ActivityPanel";
import StatusBar from "@/components/StatusBar";
import { useWebSocket } from "@/hooks/useWebSocket";
import { fetchScenarios, fetchHealth, resetSession } from "@/lib/api";
import { Scenario, ChatMessage } from "@/types";

export default function HomePage() {
  const { connected, sendMessage, events, result, error, loading, clearEvents } = useWebSocket();
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pendingInput, setPendingInput] = useState("");
  const [dbTables, setDbTables] = useState(0);
  const [responseTime, setResponseTime] = useState<number | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  // Load scenarios & health on mount
  useEffect(() => {
    fetchScenarios()
      .then(setScenarios)
      .catch(() => {
        // Fallback scenarios if backend not ready
        setScenarios([
          {
            id: "simple_query",
            title: "📊 Simple CRM Query",
            subtitle: "ค้นหาข้อมูลจาก CRM ง่ายๆ",
            description: "",
            prompt: "แสดง 5 เคสล่าสุดที่มีสถานะ Escalated",
            difficulty: "easy",
            estimated_time: "~10s",
            highlights: ["Intent Recognition", "SQL Generation"],
          },
          {
            id: "multi_step",
            title: "📋 Multi-Step Action",
            subtitle: "Agent ทำงานหลายขั้นตอน",
            description: "",
            prompt: "สรุปยอด order ของลูกค้า top 3 แล้วส่ง report ให้ทีม sales ทาง Slack",
            difficulty: "medium",
            estimated_time: "~20s",
            highlights: ["Multi-Tool", "Orchestration"],
          },
          {
            id: "error_recovery",
            title: "⚠️ Error Recovery",
            subtitle: "MCP จับ error + auto-retry",
            description: "",
            prompt: "ดึงข้อมูลเคสของ agent_id 'USR-005' ที่สร้างในเดือนนี้",
            difficulty: "advanced",
            estimated_time: "~25s",
            highlights: ["Schema Mismatch", "Auto-Recovery"],
          },
        ]);
      });

    fetchHealth()
      .then((h) => setDbTables(h.database?.tables || 0))
      .catch(() => setDbTables(0));
  }, []);

  // When result arrives, add agent message
  const prevResultRef = useRef<typeof result>(null);
  useEffect(() => {
    if (!result || result === prevResultRef.current) return;
    prevResultRef.current = result;
    const elapsed = timerRef.current
      ? (performance.now() - timerRef.current) / 1000
      : null;
    setSessionId(result.session_id);
    if (elapsed !== null) setResponseTime(elapsed);
    setMessages((prev) => [
      ...prev,
      {
        role: "agent" as const,
        content: result.agent_response,
        timestamp: Date.now(),
        result,
      },
    ]);
  }, [result]);

  // Show error as agent message
  const prevErrorRef = useRef<typeof error>(null);
  useEffect(() => {
    if (!error || error === prevErrorRef.current) return;
    prevErrorRef.current = error;
    setMessages((prev) => [
      ...prev,
      { role: "agent" as const, content: `❌ Error: ${error}`, timestamp: Date.now() },
    ]);
  }, [error]);

  const handleSend = useCallback(
    (message: string) => {
      // Add user message
      setMessages((prev) => [...prev, { role: "user", content: message, timestamp: Date.now() }]);
      setPendingInput("");
      clearEvents();
      timerRef.current = performance.now();
      sendMessage(message, sessionId || undefined);
    },
    [sendMessage, sessionId, clearEvents]
  );

  const handleReset = useCallback(async () => {
    if (sessionId) {
      try {
        await resetSession(sessionId);
      } catch {
        /* ignore */
      }
    }
    setMessages([]);
    clearEvents();
    setResponseTime(null);
    setPendingInput("");
    setSessionId(null);
    sessionStorage.removeItem("demo_session_id");
  }, [sessionId, clearEvents]);

  return (
    <div className="app-container">
      <Header connected={connected} toolCount={5} onReset={handleReset} />
      <main className="main-layout">
        <ChatPanel
          scenarios={scenarios}
          messages={messages}
          onSend={handleSend}
          loading={loading}
          pendingInput={pendingInput}
          setPendingInput={setPendingInput}
        />
        <ActivityPanel events={events} loading={loading} />
      </main>
      <StatusBar
        connected={connected}
        dbTables={dbTables}
        responseTime={responseTime}
        sessionId={sessionId}
      />
    </div>
  );
}
