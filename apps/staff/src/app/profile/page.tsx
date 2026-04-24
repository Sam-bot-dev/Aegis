"use client";

import * as React from "react";
import Link from "next/link";

export default function ProfilePage() {
  return (
    <main style={{ padding: 16, maxWidth: 640, margin: "0 auto" }}>
      <div
        style={{
          fontFamily: "JetBrains Mono, monospace",
          fontSize: 11,
          letterSpacing: "0.16em",
          color: "var(--c-ink-muted)",
        }}
      >
        AEGIS · STAFF
      </div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: "6px 0 12px" }}>Profile</h1>

      <div
        style={{
          padding: 16,
          background: "var(--c-bg-elevated)",
          border: "1px solid var(--c-border)",
          borderRadius: 12,
        }}
      >
        <div style={{ fontSize: 14, color: "var(--c-ink-secondary)" }}>
          Phone-OTP auth lands in Phase 2. For the Phase 1 judge demo, this app
          runs in read-only mode anchored to the demo venue.
        </div>
        <div style={{ marginTop: 14, fontFamily: "JetBrains Mono, monospace", fontSize: 12 }}>
          venue_id · {process.env.NEXT_PUBLIC_DEMO_VENUE_ID || "taj-ahmedabad"}
        </div>
      </div>

      <div style={{ marginTop: 40, borderTop: "1px solid var(--c-border)", paddingTop: 18 }}>
        <Link href="/" style={{ fontSize: 12, fontFamily: "JetBrains Mono, monospace" }}>
          ← INCIDENTS
        </Link>
      </div>
    </main>
  );
}
