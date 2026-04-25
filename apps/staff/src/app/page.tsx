"use client";

import * as React from "react";
import Link from "next/link";
import {
  getDb,
  IncidentCard,
  type Incident,
} from "@aegis/ui-web";
import {
  collection,
  onSnapshot,
  orderBy,
  query,
  where,
  type QueryConstraint,
} from "firebase/firestore";

const DEFAULT_VENUE_ID =
  process.env.NEXT_PUBLIC_DEMO_VENUE_ID || "taj-ahmedabad";

export default function StaffHome() {
  const [incidents, setIncidents] = React.useState<Incident[]>([]);
  const [venueId, setVenueId] = React.useState<string>(DEFAULT_VENUE_ID);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID) {
      setError(
        "Firebase not configured. Set NEXT_PUBLIC_FIREBASE_* in apps/staff/.env.local.",
      );
      return;
    }
    try {
      const db = getDb();
      const constraints: QueryConstraint[] = [
        where("venue_id", "==", venueId),
        orderBy("detected_at", "desc"),
      ];
      const q = query(collection(db, "incidents"), ...constraints);
      const unsub = onSnapshot(
        q,
        (snap) => {
          setIncidents(snap.docs.map((d) => d.data() as Incident));
        },
        (err) => setError(err.message),
      );
      return () => unsub();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [venueId]);

  const active = incidents.filter(
    (i) => !["CLOSED", "DISMISSED", "VERIFIED"].includes(i.status),
  );
  const activeIds = new Set(active.map((i) => i.incident_id));
  const recent = incidents.filter((i) => !activeIds.has(i.incident_id));

  return (
    <main style={{ padding: 16, paddingTop: 24, maxWidth: 640, margin: "0 auto" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <div>
          <div
            style={{
              fontSize: 11,
              letterSpacing: "0.16em",
              color: "var(--c-ink-muted)",
              fontFamily: "JetBrains Mono, monospace",
            }}
          >
            AEGIS · STAFF
          </div>
          <h1 style={{ margin: "6px 0 0", fontSize: 24, fontWeight: 600 }}>
            Active incidents
          </h1>
        </div>
        <select
          value={venueId}
          onChange={(e) => setVenueId(e.target.value)}
          style={{
            width: "auto",
            padding: "6px 10px",
            fontSize: 12,
            fontFamily: "JetBrains Mono, monospace",
          }}
        >
          <option value="taj-ahmedabad">taj-ahmedabad</option>
          <option value="house-of-mg">house-of-mg</option>
          <option value="demo-venue">demo-venue</option>
        </select>
      </header>

      <section style={{ marginTop: 20, display: "flex", flexDirection: "column", gap: 12 }}>
        {error ? (
          <div
            style={{
              padding: 14,
              background: "#1A0A0A",
              border: "1px solid var(--c-status-critical)",
              borderRadius: 8,
              color: "var(--c-ink-primary)",
              fontSize: 13,
            }}
          >
            {error}
          </div>
        ) : null}

        {active.length === 0 && !error ? (
          <div
            style={{
              padding: 24,
              textAlign: "center",
              color: "var(--c-ink-secondary)",
              background: "var(--c-bg-elevated)",
              border: "1px dashed var(--c-border-strong)",
              borderRadius: 12,
            }}
          >
            <div style={{ fontSize: 40, marginBottom: 6 }}>·</div>
            No active incidents. Venue nominal.
          </div>
        ) : null}

        {active.map((inc) => (
          <Link
            key={inc.incident_id}
            href={`/incident/${inc.incident_id}` as any}
            style={{ color: "inherit" }}
          >
            <IncidentCard incident={inc} />
          </Link>
        ))}
      </section>

      {recent.length > 0 ? (
        <section style={{ marginTop: 28 }}>
          <h2
            style={{
              fontSize: 11,
              letterSpacing: "0.16em",
              color: "var(--c-ink-muted)",
              fontFamily: "JetBrains Mono, monospace",
              marginBottom: 8,
            }}
          >
            RECENT
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {recent.slice(0, 10).map((inc) => (
              <Link
                key={inc.incident_id}
                href={`/incident/${inc.incident_id}` as any}
                style={{ color: "inherit" }}
              >
                <IncidentCard incident={inc} compact />
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <nav
        style={{
          marginTop: 40,
          paddingTop: 20,
          borderTop: "1px solid var(--c-border)",
          display: "flex",
          gap: 8,
          fontSize: 12,
          fontFamily: "JetBrains Mono, monospace",
          color: "var(--c-ink-muted)",
          flexWrap: "wrap",
        }}
      >
        <Link href="/drill">DRILL MODE</Link>
        <span>·</span>
        <Link href="/profile">PROFILE</Link>
        <span>·</span>
        <a href={process.env.NEXT_PUBLIC_DASHBOARD_URL || "http://localhost:3000"}>
          OPEN DASHBOARD
        </a>
      </nav>
    </main>
  );
}
