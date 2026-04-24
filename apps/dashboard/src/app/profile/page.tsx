"use client";

import * as React from "react";
import Link from "next/link";

export default function ProfilePage() {
  return (
    <main className="dashboard-shell">
      <div style={{ maxWidth: 980, margin: "0 auto", display: "grid", gap: 20 }}>
        <section className="panel" style={{ padding: 28 }}>
          <div className="eyebrow">AEGIS · DASHBOARD PROFILE</div>
          <h1 style={{ fontSize: "clamp(2rem, 1.8vw + 1.4rem, 3.2rem)", margin: "10px 0" }}>
            Venue control-room profile
          </h1>
          <p style={{ color: "var(--c-ink-secondary)", fontSize: 15, maxWidth: 720 }}>
            This surface stays intentionally simple for Phase 1. Auth, multi-venue switching,
            and roster-aware permissions land in Product Vault. For now, the dashboard is
            pinned to a demo venue so the team can show the live operations board fast.
          </p>
        </section>

        <section
          style={{
            display: "grid",
            gap: 16,
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          }}
        >
          <InfoCard
            title="Demo venue"
            value={process.env.NEXT_PUBLIC_DEMO_VENUE_ID || "taj-ahmedabad"}
            detail="Default venue currently loaded into the control-room board."
          />
          <InfoCard
            title="Staff surface"
            value={process.env.NEXT_PUBLIC_STAFF_URL || "http://localhost:3001"}
            detail="Use this during the demo when a responder needs to acknowledge the incident."
          />
          <InfoCard
            title="Dashboard mode"
            value="Read + command"
            detail="Live Firestore feed, dispatch controls, and drill shortcuts are active now."
          />
        </section>

        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <Link
            href="/"
            style={{ fontSize: 12, fontFamily: "var(--font-mono)", color: "var(--c-ink-secondary)" }}
          >
            ← Live board
          </Link>
          <Link
            href="/drill"
            style={{ fontSize: 12, fontFamily: "var(--font-mono)", color: "var(--c-ink-secondary)" }}
          >
            Open drill console →
          </Link>
        </div>
      </div>
    </main>
  );
}

function InfoCard({
  title,
  value,
  detail,
}: {
  detail: string;
  title: string;
  value: string;
}) {
  return (
    <section className="panel" style={{ padding: 20 }}>
      <div className="eyebrow">{title}</div>
      <div style={{ marginTop: 10, fontSize: 22, fontWeight: 700, wordBreak: "break-word" }}>
        {value}
      </div>
      <div style={{ marginTop: 8, color: "var(--c-ink-secondary)", fontSize: 13 }}>{detail}</div>
    </section>
  );
}
