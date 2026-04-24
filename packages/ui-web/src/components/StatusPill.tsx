import * as React from "react";
import { STATUS_COLOR, type IncidentStatus } from "../types";

export interface StatusPillProps {
  status: IncidentStatus;
}

export function StatusPill({ status }: StatusPillProps) {
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
        border: `1px solid ${STATUS_COLOR[status]}`,
        borderRadius: 999,
      }}
    >
      <span
        style={{
          width: 6,
          height: 6,
          borderRadius: 999,
          background: STATUS_COLOR[status],
        }}
      />
      {status}
    </span>
  );
}
