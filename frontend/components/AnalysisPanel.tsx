"use client";

import {
  Shield,
  AlertTriangle,
  Info,
  Zap,
  Bug,
  Target,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useState } from "react";
import RiskBadge from "./RiskBadge";

interface Analysis {
  simple_explanation: string;
  technical_explanation: string;
  infrastructure_impact: string[];
  risk_level: string;
  risk_reasons: string[];
  common_mistakes: string[];
  blast_radius_summary: string;
}

interface AnalysisPanelProps {
  analysis: Analysis | null;
}

interface CollapsibleSectionProps {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  accentColor?: string;
}

function CollapsibleSection({
  icon,
  title,
  children,
  defaultOpen = true,
  accentColor = "var(--dr-text-muted)",
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div
      className="rounded-lg overflow-hidden transition-all duration-200"
      style={{
        background: "var(--dr-bg-primary)",
        border: "1px solid var(--dr-border)",
      }}
    >
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2.5 px-4 py-3 text-left transition-colors duration-150"
        style={{ color: accentColor }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = "var(--dr-bg-tertiary)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "transparent";
        }}
      >
        {icon}
        <span className="text-xs font-semibold uppercase tracking-wider flex-1">
          {title}
        </span>
        {isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      {isOpen && (
        <div className="px-4 pb-4 animate-fade-in-up">
          {children}
        </div>
      )}
    </div>
  );
}

export default function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  if (!analysis) {
    return (
      <div className="flex flex-col h-full">
        <div className="section-header">
          <Shield size={14} />
          <span>Risk Analysis</span>
        </div>
        <div
          className="flex-1 flex flex-col items-center justify-center gap-3 rounded-lg"
          style={{ background: "var(--dr-bg-primary)", color: "var(--dr-text-muted)" }}
        >
          <Shield size={40} strokeWidth={1} />
          <p className="text-sm">AI analysis will appear here</p>
          <p className="text-xs">Risk assessment, infrastructure impact, and more</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header with Risk Badge */}
      <div className="flex items-center justify-between mb-3">
        <div className="section-header mb-0 pb-0 border-b-0">
          <Shield size={14} />
          <span>Risk Analysis</span>
        </div>
        <RiskBadge level={analysis.risk_level} />
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {/* Simple Explanation */}
        <CollapsibleSection
          icon={<Info size={14} />}
          title="What This Does"
          accentColor="var(--dr-accent-cyan)"
        >
          <p className="text-sm leading-relaxed" style={{ color: "var(--dr-text-secondary)" }}>
            {analysis.simple_explanation}
          </p>
        </CollapsibleSection>

        {/* Technical Explanation */}
        <CollapsibleSection
          icon={<Zap size={14} />}
          title="Technical Details"
          defaultOpen={false}
          accentColor="var(--dr-accent-blue)"
        >
          <p className="text-sm leading-relaxed" style={{ color: "var(--dr-text-secondary)" }}>
            {analysis.technical_explanation}
          </p>
        </CollapsibleSection>

        {/* Infrastructure Impact */}
        {analysis.infrastructure_impact.length > 0 && (
          <CollapsibleSection
            icon={<Target size={14} />}
            title="Infrastructure Impact"
            accentColor="var(--dr-accent-teal)"
          >
            <ul className="space-y-1.5">
              {analysis.infrastructure_impact.map((impact, i) => (
                <li key={i} className="flex items-start gap-2 text-sm"
                  style={{ color: "var(--dr-text-secondary)" }}>
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ background: "var(--dr-accent-teal)" }} />
                  {impact}
                </li>
              ))}
            </ul>
          </CollapsibleSection>
        )}

        {/* Risk Reasons */}
        {analysis.risk_reasons.length > 0 && (
          <CollapsibleSection
            icon={<AlertTriangle size={14} />}
            title="Risk Factors"
            accentColor="var(--dr-risk-medium)"
          >
            <ul className="space-y-1.5">
              {analysis.risk_reasons.map((reason, i) => (
                <li key={i} className="flex items-start gap-2 text-sm"
                  style={{ color: "var(--dr-text-secondary)" }}>
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ background: "var(--dr-risk-medium)" }} />
                  {reason}
                </li>
              ))}
            </ul>
          </CollapsibleSection>
        )}

        {/* Common Mistakes */}
        {analysis.common_mistakes.length > 0 && (
          <CollapsibleSection
            icon={<Bug size={14} />}
            title="Common Mistakes"
            defaultOpen={false}
            accentColor="var(--dr-risk-high)"
          >
            <ul className="space-y-1.5">
              {analysis.common_mistakes.map((mistake, i) => (
                <li key={i} className="flex items-start gap-2 text-sm"
                  style={{ color: "var(--dr-text-secondary)" }}>
                  <span className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ background: "var(--dr-risk-high)" }} />
                  {mistake}
                </li>
              ))}
            </ul>
          </CollapsibleSection>
        )}

        {/* Blast Radius */}
        {analysis.blast_radius_summary && (
          <div
            className="rounded-lg p-4 animate-fade-in-up"
            style={{
              background: "linear-gradient(135deg, rgba(6, 182, 212, 0.05), rgba(20, 184, 166, 0.05))",
              border: "1px solid rgba(6, 182, 212, 0.2)",
            }}
          >
            <div className="flex items-center gap-2 mb-2">
              <Target size={14} style={{ color: "var(--dr-accent-cyan)" }} />
              <span className="text-xs font-semibold uppercase tracking-wider"
                style={{ color: "var(--dr-accent-cyan)" }}>
                Blast Radius
              </span>
            </div>
            <p className="text-sm leading-relaxed" style={{ color: "var(--dr-text-secondary)" }}>
              {analysis.blast_radius_summary}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
