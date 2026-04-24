import * as React from "react";
import type { Incident } from "../types";
import { SeverityBadge } from "./SeverityBadge";
import { StatusPill } from "./StatusPill";

export interface IncidentCardProps {
  incident: Incident;
  onClick?: () => void;
  compact?: boolean;
}

function formatElapsed(iso: string): string {
  const d = new Date(iso);
  const s = Math.max(0, (Date.now() - d.getTime()) / 1000);
  if (s < 60) return `${Math.floor(s)}s`;
  if (s < 3600) return `${Math.floor(s / 60)}m ${Math.floor(s % 60)}s`;
  return `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`;
}

export function IncidentCard({ incident, onClick, compact }: IncidentCardProps) {
  const sev = incident.classification?.severity ?? "S4";
  const category = incident.classification?.category ?? "OTHER";
  return (
    <div
      onClick={onClick}
      role={onClick ? "button" : undefined}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 10,
        padding: compact ? 14 : 18,
        background: "#121821",
        border: "1px solid #1E293B",
        borderRadius: 12,
        cursor: onClick ? "pointer" : "default",
        color: "#F1F5F9",
        fontFamily: "Inter, system-ui, sans-serif",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <SeverityBadge severity={sev} size={compact ? "sm" : "md"} />
          <StatusPill status={incident.status} />
        </div>
        <span
          style={{
            fontFamily: "JetBrains Mono, monospace",
            fontSize: 12,
            color: "#94A3B8",
          }}
        >
          {formatElapsed(incident.detected_at)}
        </span>
      </div>
      <div style={{ fontSize: compact ? 16 : 20, fontWeight: 600 }}>
        {category}
        {incident.classification?.sub_type ? (
          <span style={{ color: "#94A3B8", fontWeight: 400 }}>
            {" "}
            · {incident.classification.sub_type}
          </span>
        ) : null}
      </div>
      <div style={{ color: "#94A3B8", fontSize: 13 }}>
        {incident.summary || incident.classification?.rationale || "—"}
      </div>
      <div style={{ display: "flex", gap: 12, fontSize: 12, color: "#64748B" }}>
        <span style={{ fontFamily: "JetBrains Mono, monospace" }}>{incident.incident_id}</span>
        <span>zone: {incident.zone_id}</span>
      </div>
    </div>
  );
}
