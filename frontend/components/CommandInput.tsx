"use client";

import { useState } from "react";
import { Terminal, Play, Loader2 } from "lucide-react";

interface CommandInputProps {
  onAnalyze: (command: string) => void;
  isLoading: boolean;
  command: string;
  setCommand: (cmd: string) => void;
}

const EXAMPLE_COMMANDS = [
  "docker run -p 80:80 nginx",
  "docker run -d --name myapp -p 3000:3000 -v ./data:/app/data node:18",
  "docker build -t myapp:latest .",
  "docker exec -it mycontainer bash",
  "docker network create my-network",
  "docker volume create my-data",
  "docker stop mycontainer",
  "docker rm mycontainer",
];

export default function CommandInput({ onAnalyze, isLoading, command, setCommand }: CommandInputProps) {

  const handleSubmit = () => {
    const trimmed = command.trim();
    if (trimmed && !isLoading) {
      onAnalyze(trimmed);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      handleSubmit();
    }
  };

  const handleExampleClick = (example: string) => {
    setCommand(example);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="section-header">
        <Terminal size={14} />
        <span>Docker Command</span>
      </div>

      {/* Input */}
      <textarea
        id="command-input"
        className="dr-textarea flex-1"
        value={command}
        onChange={(e) => setCommand(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Enter a Docker command to analyze..."
        spellCheck={false}
        disabled={isLoading}
      />

      {/* Keyboard hint */}
      <div className="mt-2 text-xs" style={{ color: "var(--dr-text-muted)" }}>
        Press <kbd className="px-1.5 py-0.5 rounded text-[10px] font-mono"
          style={{ background: "var(--dr-bg-secondary)", border: "1px solid var(--dr-border)" }}>
          Ctrl+Enter
        </kbd> to analyze
      </div>

      {/* Analyze Button */}
      <button
        id="analyze-button"
        className="dr-button-primary mt-3 w-full flex items-center justify-center gap-2"
        onClick={handleSubmit}
        disabled={!command.trim() || isLoading}
      >
        {isLoading ? (
          <>
            <Loader2 size={16} className="animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Play size={16} />
            Analyze Command
          </>
        )}
      </button>

      {/* Example Commands */}
      <div className="mt-4">
        <div className="text-xs font-medium mb-2" style={{ color: "var(--dr-text-muted)" }}>
          Quick examples:
        </div>
        <div className="flex flex-col gap-1.5">
          {EXAMPLE_COMMANDS.map((ex) => (
            <button
              key={ex}
              onClick={() => handleExampleClick(ex)}
              className="text-left text-xs px-3 py-2 rounded-md transition-all duration-150 font-mono truncate"
              style={{
                background: "var(--dr-bg-primary)",
                border: "1px solid var(--dr-border)",
                color: "var(--dr-text-secondary)",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "var(--dr-accent-cyan)";
                e.currentTarget.style.color = "var(--dr-accent-cyan)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "var(--dr-border)";
                e.currentTarget.style.color = "var(--dr-text-secondary)";
              }}
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
