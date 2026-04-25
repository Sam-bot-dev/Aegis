import * as React from "react";
import {
  DISPATCH_STATUS_COLOR,
  STATUS_COLOR,
  type DispatchStatus,
  type IncidentStatus,
} from "../types";

export interface StatusPillProps {
  status: IncidentStatus | DispatchStatus;
}

const FALLBACK_COLOR = "#64748B";

function colorFor(status: IncidentStatus | DispatchStatus): string {
  return (
    (STATUS_COLOR as Record<string, string>)[status] ||
    (DISPATCH_STATUS_COLOR as Record<string, string>)[status] ||
    FALLBACK_COLOR
  );
}

export function StatusPill({ status }: StatusPillProps) {
  const color = colorFor(status);
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "4px 10px",
        fontSize: 12,
        fontFamily: "JetBrains Mono, ui-monospace, monospace",
        letterSpacing: "0.06em",
        color: "#F1F5F9",
        background: "rgba(255,255,255,0.04)",
        border: `1px solid ${color}`,
        borderRadius: 999,
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: 999,
          background: color,
        }}
      />
      {status}
    </span>
  );
}
