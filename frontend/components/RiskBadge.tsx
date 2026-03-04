"use client";

interface RiskBadgeProps {
  level: string;
}

const RISK_CONFIG: Record<string, { color: string; bg: string; border: string; label: string }> = {
  low: {
    color: "var(--dr-risk-low)",
    bg: "rgba(34, 197, 94, 0.1)",
    border: "rgba(34, 197, 94, 0.3)",
    label: "LOW RISK",
  },
  medium: {
    color: "var(--dr-risk-medium)",
    bg: "rgba(245, 158, 11, 0.1)",
    border: "rgba(245, 158, 11, 0.3)",
    label: "MEDIUM RISK",
  },
  high: {
    color: "var(--dr-risk-high)",
    bg: "rgba(239, 68, 68, 0.1)",
    border: "rgba(239, 68, 68, 0.3)",
    label: "HIGH RISK",
  },
};

export default function RiskBadge({ level }: RiskBadgeProps) {
  const normalizedLevel = level?.toLowerCase() || "medium";
  const config = RISK_CONFIG[normalizedLevel] || RISK_CONFIG.medium;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold tracking-wider ${
        normalizedLevel === "high" ? "animate-risk-pulse" : ""
      }`}
      style={{
        color: config.color,
        background: config.bg,
        border: `1px solid ${config.border}`,
      }}
    >
      <span
        className="w-2 h-2 rounded-full"
        style={{ background: config.color }}
      />
      {config.label}
    </span>
  );
}
