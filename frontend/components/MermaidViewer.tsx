"use client";

import { useEffect, useRef, useCallback } from "react";
import mermaid from "mermaid";
import { GitBranch } from "lucide-react";

interface MermaidViewerProps {
  diagram: string | null;
}

export default function MermaidViewer({ diagram }: MermaidViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const renderIdRef = useRef(0);

  const renderDiagram = useCallback(async () => {
    if (!containerRef.current || !diagram) return;

    const currentRenderId = ++renderIdRef.current;

    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: "dark",
        themeVariables: {
          darkMode: true,
          background: "#151d2b",
          primaryColor: "#0f766e",
          primaryTextColor: "#e2e8f0",
          primaryBorderColor: "#14b8a6",
          lineColor: "#475569",
          secondaryColor: "#1d4ed8",
          tertiaryColor: "#1a2332",
          fontFamily: "Inter, sans-serif",
          fontSize: "14px",
        },
        flowchart: {
          htmlLabels: true,
          curve: "basis",
          padding: 16,
          nodeSpacing: 50,
          rankSpacing: 60,
        },
        securityLevel: "strict",
      });

      // Clear previous diagram
      containerRef.current.innerHTML = "";

      const elementId = `mermaid-${currentRenderId}`;
      const { svg } = await mermaid.render(elementId, diagram);

      // Only update if this is still the latest render
      if (currentRenderId === renderIdRef.current && containerRef.current) {
        containerRef.current.innerHTML = svg;
      }
    } catch (err) {
      console.error("Mermaid render error:", err);
      if (currentRenderId === renderIdRef.current && containerRef.current) {
        containerRef.current.innerHTML = `
          <div style="padding: 24px; color: var(--dr-risk-medium); font-size: 0.875rem;">
            <p style="font-weight: 600;">Diagram Render Error</p>
            <p style="margin-top: 8px; color: var(--dr-text-muted); font-size: 0.75rem;">
              The generated diagram could not be rendered. This may indicate a malformed Mermaid syntax.
            </p>
          </div>
        `;
      }
    }
  }, [diagram]);

  useEffect(() => {
    renderDiagram();
  }, [renderDiagram]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="section-header">
        <GitBranch size={14} />
        <span>Infrastructure Diagram</span>
      </div>

      {/* Diagram */}
      <div className="flex-1 overflow-auto rounded-lg" style={{ background: "var(--dr-bg-primary)" }}>
        {diagram ? (
          <div
            ref={containerRef}
            className="mermaid-container p-4 flex items-center justify-center min-h-[200px] animate-fade-in-up"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full min-h-[200px] gap-3"
            style={{ color: "var(--dr-text-muted)" }}>
            <GitBranch size={40} strokeWidth={1} />
            <p className="text-sm">Enter a Docker command to visualize</p>
            <p className="text-xs">Infrastructure diagram will appear here</p>
          </div>
        )}
      </div>
    </div>
  );
}
