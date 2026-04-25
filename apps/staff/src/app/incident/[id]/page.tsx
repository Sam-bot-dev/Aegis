"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  getDb,
  SeverityBadge,
  StatusPill,
  CountdownRing,
  SEVERITY_COLOR,
  type Dispatch,
  type Incident,
  type IncidentEvent,
} from "@aegis/ui-web";
import {
  collection,
  doc,
  onSnapshot,
  orderBy,
  query,
} from "firebase/firestore";

const DISPATCH_BASE =
  process.env.NEXT_PUBLIC_DISPATCH_URL || "http://localhost:8004";
const ACK_COUNTDOWN_SECONDS = 15;

export default function IncidentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = params?.id ?? "";

  const [incident, setIncident] = React.useState<Incident | null>(null);
  const [dispatches, setDispatches] = React.useState<Dispatch[]>([]);
  const [events, setEvents] = React.useState<IncidentEvent[]>([]);
  const [acking, setAcking] = React.useState(false);
  const [countdownKey, setCountdownKey] = React.useState(0);
  const [traceOpen, setTraceOpen] = React.useState(false);

  React.useEffect(() => {
    if (!id || !process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID) return;
    const db = getDb();
    const unsubI = onSnapshot(doc(db, "incidents", id), (snap) => {
      if (snap.exists()) setIncident(snap.data() as Incident);
    });
    const unsubD = onSnapshot(
      query(
        collection(db, "incidents", id, "dispatches"),
        orderBy("paged_at", "asc"),
      ),
      (snap) => setDispatches(snap.docs.map((d) => d.data() as Dispatch)),
    );
    const unsubE = onSnapshot(
      query(
        collection(db, "incidents", id, "events"),
        orderBy("event_time", "asc"),
      ),
      (snap) => setEvents(snap.docs.map((d) => d.data() as IncidentEvent)),
    );
    return () => {
      unsubI();
      unsubD();
      unsubE();
    };
  }, [id]);

  const loaded = incident !== null;
  const severity = incident?.classification?.severity ?? "S4";
  const category = incident?.classification?.category ?? "OTHER";
  const primary = dispatches[0];

  async function act(path: string) {
    if (!primary) return;
    setAcking(true);
    try {
      await fetch(`${DISPATCH_BASE}/v1/dispatches/${primary.dispatch_id}/${path}`, {
        method: "POST",
      });
      setCountdownKey((k) => k + 1);
    } finally {
      setAcking(false);
    }
  }

  const emergencyBg = severity === "S1" ? "#1A0A0A" : "var(--c-bg-primary)";

  if (!loaded) {
    return (
      <main
        style={{
          minHeight: "100vh",
          background: "var(--c-bg-primary)",
          padding: 16,
          maxWidth: 640,
          margin: "0 auto",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--c-ink-muted)",
          fontFamily: "JetBrains Mono, monospace",
          fontSize: 13,
          letterSpacing: "0.08em",
        }}
      >
        LOADING INCIDENT…
      </main>
    );
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        background: emergencyBg,
        padding: 16,
        maxWidth: 640,
        margin: "0 auto",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <button
          onClick={() => router.back()}
          aria-label="back"
          style={{
            background: "transparent",
            border: "none",
            color: "var(--c-ink-secondary)",
            fontSize: 24,
            padding: 4,
          }}
        >
          ‹
        </button>
        <span
          style={{
            fontFamily: "JetBrains Mono, monospace",
            color: "var(--c-ink-muted)",
            fontSize: 12,
          }}
        >
          {id}
        </span>
        <div style={{ flex: 1 }} />
        <SeverityBadge severity={severity} size="sm" />
      </div>

      <h1 style={{ marginTop: 18, fontSize: 36, fontWeight: 700, letterSpacing: -0.5 }}>
        {category}
      </h1>
      <div style={{ color: "var(--c-ink-secondary)", marginTop: 4 }}>
        {incident?.zone_id ? `Zone · ${incident.zone_id}` : "Zone · —"}
      </div>

      <div
        style={{
          marginTop: 20,
          padding: 16,
          background: "var(--c-bg-elevated)",
          border: `1px solid ${SEVERITY_COLOR[severity]}`,
          borderRadius: 12,
          display: "flex",
          gap: 14,
          alignItems: "center",
        }}
        className={severity === "S1" ? "pulse-urgent" : undefined}
      >
        {primary && primary.status === "PAGED" ? (
          <>
            <CountdownRing
              key={countdownKey}
              totalSeconds={ACK_COUNTDOWN_SECONDS}
              color={SEVERITY_COLOR[severity]}
              onComplete={() => void 0}
              size={56}
            />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 11, letterSpacing: "0.12em", color: "var(--c-ink-muted)" }}>
                YOUR ACTION
              </div>
              <div style={{ fontSize: 17, fontWeight: 600, marginTop: 2 }}>
                {primary.notes || "Proceed to location"}
              </div>
              <div style={{ fontSize: 12, color: "var(--c-ink-secondary)", marginTop: 4 }}>
                Auto-escalates in {ACK_COUNTDOWN_SECONDS}s
              </div>
            </div>
          </>
        ) : (
          <div style={{ flex: 1, color: "var(--c-ink-secondary)" }}>
            {primary ? `Status: ${primary.status}` : "No dispatch yet"}
          </div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 12 }}>
        <button
          disabled={!primary || acking || primary.status !== "PAGED"}
          onClick={() => act("ack")}
          style={primaryBtn(SEVERITY_COLOR[severity])}
        >
          CLAIM
        </button>
        <button
          disabled={
            !primary ||
            acking ||
            (primary.status !== "PAGED" &&
              primary.status !== "ACKNOWLEDGED" &&
              primary.status !== "EN_ROUTE")
          }
          onClick={() => act("decline")}
          style={secondaryBtn}
        >
          Decline
        </button>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 8 }}>
        <button
          disabled={!primary || acking || primary.status !== "ACKNOWLEDGED"}
          onClick={() => act("enroute")}
          style={secondaryBtn}
        >
          En route
        </button>
        <button
          disabled={!primary || acking || primary.status !== "EN_ROUTE"}
          onClick={() => act("arrived")}
          style={secondaryBtn}
        >
          Arrived
        </button>
      </div>

      <Section title="DISPATCHED">
        {dispatches.length === 0 ? (
          <div style={{ color: "var(--c-ink-muted)", fontSize: 13 }}>
            No responders paged yet.
          </div>
        ) : (
          dispatches.map((d) => (
            <div
              key={d.dispatch_id}
              style={{
                display: "flex",
                gap: 10,
                padding: "10px 0",
                borderBottom: "1px solid var(--c-border)",
              }}
            >
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14 }}>
                  {d.role} · <span style={{ color: "var(--c-ink-secondary)" }}>{d.responder_id}</span>
                </div>
                <div style={{ fontSize: 12, color: "var(--c-ink-muted)", marginTop: 2 }}>
                  {d.notes || "—"}
                </div>
              </div>
              <StatusPill status={d.status} />
            </div>
          ))
        )}
      </Section>

      {incident?.classification?.cascade_predictions?.length ? (
        <Section title="CASCADE FORECAST">
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {incident.classification.cascade_predictions.map((c, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontSize: 13,
                  color: "var(--c-ink-primary)",
                }}
              >
                <span>
                  <span style={{ color: "var(--c-ink-muted)", fontFamily: "JetBrains Mono, monospace", marginRight: 8 }}>
                    +{c.horizon_seconds}s
                  </span>
                  {c.outcome}
                </span>
                <span style={{ fontFamily: "JetBrains Mono, monospace" }}>
                  {(c.probability * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </Section>
      ) : null}

      <Section title="AGENT TRACE">
        <button
          onClick={() => setTraceOpen((v) => !v)}
          style={{
            background: "transparent",
            border: "1px solid var(--c-border)",
            color: "var(--c-ink-secondary)",
            padding: "8px 12px",
            borderRadius: 8,
            fontSize: 12,
            fontFamily: "JetBrains Mono, monospace",
          }}
        >
          {traceOpen ? "hide trace ▴" : "view full trace ▾"}
        </button>
        {traceOpen ? (
          <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 6 }}>
            {events.map((e) => (
              <div
                key={e.event_id}
                style={{
                  fontFamily: "JetBrains Mono, monospace",
                  fontSize: 11.5,
                  color: "var(--c-ink-secondary)",
                }}
              >
                <span style={{ color: "var(--c-ink-muted)" }}>
                  {new Date(e.event_time).toISOString().slice(11, 19)}
                </span>{" "}
                {e.from_status ?? "·"} → {e.to_status} by {e.actor_id}
              </div>
            ))}
          </div>
        ) : null}
      </Section>

      <footer style={{ marginTop: 40, paddingTop: 18, borderTop: "1px solid var(--c-border)" }}>
        <Link href="/" style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace" }}>
          ← ALL INCIDENTS
        </Link>
      </footer>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ marginTop: 26 }}>
      <div
        style={{
          fontSize: 11,
          letterSpacing: "0.16em",
          color: "var(--c-ink-muted)",
          fontFamily: "JetBrains Mono, monospace",
          marginBottom: 10,
        }}
      >
        {title}
      </div>
      {children}
    </section>
  );
}

function primaryBtn(color: string): React.CSSProperties {
  return {
    background: color,
    color: "#F8FAFC",
    border: "none",
    borderRadius: 10,
    padding: "16px 18px",
    fontSize: 16,
    fontWeight: 600,
    letterSpacing: "0.02em",
  };
}

const secondaryBtn: React.CSSProperties = {
  background: "transparent",
  color: "var(--c-ink-primary)",
  border: "1px solid var(--c-border-strong)",
  borderRadius: 10,
  padding: "14px 18px",
  fontSize: 15,
};
