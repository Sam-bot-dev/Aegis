import * as React from "react";
import { SEVERITY_COLOR, type Severity } from "../types";

export interface SeverityBadgeProps {
  severity: Severity;
  size?: "sm" | "md" | "lg";
}

const LABEL: Record<Severity, string> = {
  S1: "S1 · CRITICAL",
  S2: "S2 · URGENT",
  S3: "S3 · MONITOR",
  S4: "S4 · NUISANCE",
};

export function SeverityBadge({ severity, size = "md" }: SeverityBadgeProps) {
  const color = SEVERITY_COLOR[severity];
  const px = size === "lg" ? "12px 18px" : size === "sm" ? "3px 8px" : "6px 12px";
  const fontSize = size === "lg" ? 16 : size === "sm" ? 11 : 13;
  return (
    <span
      style={{
        display: "inline-block",
        padding: px,
        fontFamily: "JetBrains Mono, ui-monospace, monospace",
        fontSize,
        letterSpacing: "0.04em",
        color: "#F8FAFC",
        background: color,
        borderRadius: 999,
        fontWeight: 600,
      }}
    >
      {LABEL[severity]}
    </span>
  );
}
