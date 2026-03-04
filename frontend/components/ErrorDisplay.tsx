"use client";

import { AlertTriangle, Sparkles, ArrowRight } from "lucide-react";

interface ErrorDisplayProps {
  error: string;
  command?: string;
  suggestion?: string | null;
  supportedCommands?: string[];
  onUseSuggestion?: (cmd: string) => void;
}

export default function ErrorDisplay({ 
  error, 
  command, 
  suggestion, 
  supportedCommands,
  onUseSuggestion 
}: ErrorDisplayProps) {
  return (
    <div
      className="dr-card p-5 animate-fade-in-up"
      style={{ borderColor: "rgba(239, 68, 68, 0.3)" }}
    >
      <div className="flex items-start gap-3">
        <div
          className="p-2 rounded-lg shrink-0"
          style={{ background: "rgba(239, 68, 68, 0.1)" }}
        >
          <AlertTriangle size={18} style={{ color: "var(--dr-risk-high)" }} />
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold" style={{ color: "var(--dr-risk-high)" }}>
            Analysis Error
          </p>
          <p className="text-sm mt-1" style={{ color: "var(--dr-text-secondary)" }}>
            {error}
          </p>

          {command && (
            <div className="mt-3">
              <p className="text-xs font-medium mb-1.5" style={{ color: "var(--dr-text-muted)" }}>
                Failed command:
              </p>
              <code
                className="block text-xs p-2 rounded font-mono overflow-x-auto"
                style={{
                  background: "var(--dr-bg-primary)",
                  border: "1px solid var(--dr-border)",
                  color: "var(--dr-risk-high)",
                }}
              >
                {command}
              </code>
            </div>
          )}

          {suggestion && (
            <div className="mt-4 p-3 rounded-lg border animate-pulse-subtle"
              style={{ 
                background: "rgba(20, 184, 166, 0.05)", 
                borderColor: "rgba(20, 184, 166, 0.2)" 
              }}
            >
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={14} style={{ color: "var(--dr-accent-cyan)" }} />
                <p className="text-xs font-semibold" style={{ color: "var(--dr-accent-cyan)" }}>
                  AI Suggestion
                </p>
              </div>
              <code
                className="block text-xs p-2 rounded font-mono mb-3"
                style={{
                  background: "var(--dr-bg-primary)",
                  border: "1px solid var(--dr-border)",
                  color: "var(--dr-text-primary)",
                }}
              >
                {suggestion}
              </code>
              <button
                onClick={() => onUseSuggestion?.(suggestion)}
                className="flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded transition-all hover:scale-105 active:scale-95"
                style={{
                  background: "var(--dr-accent-cyan)",
                  color: "var(--dr-bg-primary)",
                }}
              >
                Use this instead
                <ArrowRight size={14} />
              </button>
            </div>
          )}

          {supportedCommands && supportedCommands.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium mb-2" style={{ color: "var(--dr-text-muted)" }}>
                Supported commands:
              </p>
              <div className="flex flex-wrap gap-1.5">
                {supportedCommands.map((cmd) => (
                  <code
                    key={cmd}
                    className="text-xs px-2 py-1 rounded font-mono"
                    style={{
                      background: "var(--dr-bg-primary)",
                      border: "1px solid var(--dr-border)",
                      color: "var(--dr-accent-cyan)",
                    }}
                  >
                    {cmd}
                  </code>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
