"use client";

import { useState } from "react";
import axios from "axios";
import { Radar, Github } from "lucide-react";
import CommandInput from "@/components/CommandInput";
import MermaidViewer from "@/components/MermaidViewer";
import AnalysisPanel from "@/components/AnalysisPanel";
import ErrorDisplay from "@/components/ErrorDisplay";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Analysis {
  simple_explanation: string;
  technical_explanation: string;
  infrastructure_impact: string[];
  risk_level: string;
  risk_reasons: string[];
  common_mistakes: string[];
  blast_radius_summary: string;
}

interface AnalyzeResponse {
  mermaid: string;
  analysis: Analysis;
}

interface ApiError {
  error: string;
  supported_commands?: string[];
}

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [mermaidDiagram, setMermaidDiagram] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const handleAnalyze = async (command: string) => {
    setIsLoading(true);
    setError(null);
    setMermaidDiagram(null);
    setAnalysis(null);

    try {
      const response = await axios.post<AnalyzeResponse>(`${API_URL}/analyze`, {
        command,
      });

      setMermaidDiagram(response.data.mermaid);
      setAnalysis(response.data.analysis);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response) {
        const data = err.response.data as ApiError;
        setError({
          error: data.error || "An unexpected error occurred",
          supported_commands: data.supported_commands,
        });
      } else {
        setError({
          error: "Failed to connect to the analysis server. Make sure the backend is running on port 8000.",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col" style={{ background: "var(--dr-bg-primary)" }}>
      {/* ─── Top Bar ─────────────────────────────────────────── */}
      <header
        className="flex items-center justify-between px-6 py-3 shrink-0"
        style={{
          background: "var(--dr-bg-secondary)",
          borderBottom: "1px solid var(--dr-border)",
        }}
      >
        <div className="flex items-center gap-3">
          <div
            className="p-1.5 rounded-lg"
            style={{
              background: "linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(20, 184, 166, 0.15))",
            }}
          >
            <Radar size={20} style={{ color: "var(--dr-accent-cyan)" }} />
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight" style={{ color: "var(--dr-text-primary)" }}>
              DockRadius
            </h1>
            <p className="text-[10px] tracking-widest uppercase" style={{ color: "var(--dr-text-muted)" }}>
              Docker Blast Radius Analyzer
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-xs px-2.5 py-1 rounded-full font-medium"
            style={{
              background: "rgba(6, 182, 212, 0.1)",
              color: "var(--dr-accent-cyan)",
              border: "1px solid rgba(6, 182, 212, 0.2)",
            }}>
            v1.0
          </span>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors duration-150"
            style={{ color: "var(--dr-text-muted)" }}
            onMouseEnter={(e) => { e.currentTarget.style.color = "var(--dr-text-primary)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = "var(--dr-text-muted)"; }}
          >
            <Github size={18} />
          </a>
        </div>
      </header>

      {/* ─── Main Content ────────────────────────────────────── */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Panel — Command Input */}
        <aside
          className="w-[340px] shrink-0 p-4 overflow-y-auto"
          style={{
            background: "var(--dr-bg-secondary)",
            borderRight: "1px solid var(--dr-border)",
          }}
        >
          <CommandInput onAnalyze={handleAnalyze} isLoading={isLoading} />
        </aside>

        {/* Right Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Error Banner */}
          {error && (
            <div className="p-4 shrink-0">
              <ErrorDisplay error={error.error} supportedCommands={error.supported_commands} />
            </div>
          )}

          {/* Loading shimmer */}
          {isLoading && (
            <div className="p-4 shrink-0">
              <div className="dr-card p-6 animate-shimmer">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full animate-spin"
                    style={{ border: "2px solid var(--dr-border)", borderTopColor: "var(--dr-accent-cyan)" }} />
                  <span className="text-sm" style={{ color: "var(--dr-text-muted)" }}>
                    Analyzing Docker command...
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Diagram + Analysis Split */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Top — Mermaid Diagram */}
            <div
              className="flex-1 p-4 overflow-hidden"
              style={{ minHeight: "40%" }}
            >
              <div className="dr-card h-full p-4">
                <MermaidViewer diagram={mermaidDiagram} />
              </div>
            </div>

            {/* Bottom — Analysis Panel */}
            <div
              className="flex-1 p-4 pt-0 overflow-hidden"
              style={{ minHeight: "40%" }}
            >
              <div className="dr-card h-full p-4 overflow-y-auto">
                <AnalysisPanel analysis={analysis} />
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* ─── Footer ──────────────────────────────────────────── */}
      <footer
        className="flex items-center justify-center px-6 py-2 shrink-0"
        style={{
          background: "var(--dr-bg-secondary)",
          borderTop: "1px solid var(--dr-border)",
        }}
      >
        <p className="text-[11px]" style={{ color: "var(--dr-text-muted)" }}>
          DockRadius — Static analysis only. No Docker commands are ever executed.
        </p>
      </footer>
    </div>
  );
}
