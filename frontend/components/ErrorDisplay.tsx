"use client";

import { AlertTriangle } from "lucide-react";

interface ErrorDisplayProps {
  error: string;
  supportedCommands?: string[];
}

export default function ErrorDisplay({ error, supportedCommands }: ErrorDisplayProps) {
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
