"use client";

import { useRef, useState, useCallback, useEffect } from "react";
import { StepEvent, ChatResult } from "@/types";
import { createChatWebSocket } from "@/lib/api";

interface UseWebSocketReturn {
  connected: boolean;
  sendMessage: (message: string, sessionId?: string) => void;
  events: StepEvent[];
  result: ChatResult | null;
  error: string | null;
  loading: boolean;
  clearEvents: () => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<StepEvent[]>([]);
  const [result, setResult] = useState<ChatResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = createChatWebSocket();

    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      // Auto-reconnect after 2s
      setTimeout(connect, 2000);
    };
    ws.onerror = () => setConnected(false);

    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);

        if (data.type === "session") {
          // Session ID assigned — store for later
          if (typeof window !== "undefined") {
            sessionStorage.setItem("demo_session_id", data.session_id);
          }
        } else if (data.type === "event") {
          setEvents((prev) => [...prev, data as StepEvent]);
        } else if (data.type === "result") {
          setResult(data as ChatResult);
          setLoading(false);
        } else if (data.type === "error") {
          setError(data.error || "Unknown error");
          setLoading(false);
        }
      } catch {
        // ignore malformed messages
      }
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const sendMessage = useCallback(
    (message: string, sessionId?: string) => {
      if (wsRef.current?.readyState !== WebSocket.OPEN) {
        setError("WebSocket not connected");
        return;
      }
      setEvents([]);
      setResult(null);
      setError(null);
      setLoading(true);

      wsRef.current.send(
        JSON.stringify({
          message,
          session_id:
            sessionId ||
            (typeof window !== "undefined"
              ? sessionStorage.getItem("demo_session_id")
              : null),
        })
      );
    },
    []
  );

  const clearEvents = useCallback(() => {
    setEvents([]);
    setResult(null);
    setError(null);
  }, []);

  return { connected, sendMessage, events, result, error, loading, clearEvents };
}
