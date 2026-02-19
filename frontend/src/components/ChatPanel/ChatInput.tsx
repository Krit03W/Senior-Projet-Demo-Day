"use client";

import React, { useState, useRef, useEffect } from "react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  initialValue?: string;
}

export default function ChatInput({ onSend, disabled, initialValue }: ChatInputProps) {
  const [value, setValue] = useState(initialValue || "");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (initialValue) setValue(initialValue);
  }, [initialValue]);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-wrapper">
      <textarea
        ref={inputRef}
        className="chat-input"
        placeholder="พิมพ์คำถาม CRM ของคุณ..."
        rows={2}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
      />
      <button
        className="send-btn"
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
      >
        {disabled ? (
          <span className="loading-spinner" />
        ) : (
          "➤"
        )}
      </button>
    </div>
  );
}
