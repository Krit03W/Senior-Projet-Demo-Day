"use client";

import React from "react";
import { Scenario, ChatMessage } from "@/types";
import ScenarioCards from "./ScenarioCards";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

interface ChatPanelProps {
  scenarios: Scenario[];
  messages: ChatMessage[];
  onSend: (message: string) => void;
  loading: boolean;
  pendingInput: string;
  setPendingInput: (v: string) => void;
}

export default function ChatPanel({
  scenarios,
  messages,
  onSend,
  loading,
  pendingInput,
  setPendingInput,
}: ChatPanelProps) {
  const handleScenarioSelect = (prompt: string) => {
    setPendingInput(prompt);
    onSend(prompt);
  };

  return (
    <div className="chat-panel">
      <div className="panel-header">
        <h2>💬 Chat</h2>
      </div>
      {messages.length === 0 && (
        <ScenarioCards
          scenarios={scenarios}
          onSelect={handleScenarioSelect}
          disabled={loading}
        />
      )}
      <MessageList messages={messages} />
      <ChatInput
        onSend={onSend}
        disabled={loading}
        initialValue={pendingInput}
      />
    </div>
  );
}
