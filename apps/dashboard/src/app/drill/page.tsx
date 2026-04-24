"use client";

import * as React from "react";
import Link from "next/link";

const INGEST_BASE =
  process.env.NEXT_PUBLIC_INGEST_URL || "http://localhost:8001";
const VISION_BASE =
  process.env.NEXT_PUBLIC_VISION_URL || "http://localhost:8002";
const ORCH_BASE =
  process.env.NEXT_PUBLIC_ORCHESTRATOR_URL || "http://localhost:8003";
const VENUE = process.env.NEXT_PUBLIC_DEMO_VENUE_ID || "taj-ahmedabad";

type Step = { label: string; status: "pending" | "running" | "ok" | "error"; detail?: string };

export default function DrillPage() {
  const [steps, setSteps] = React.useState<Step[]>([]);
  const [running, setRunning] = React.useState(false);

  function update(i: number, patch: Partial<Step>) {
    setSteps((s) => s.map((step, idx) => (idx === i ? { ...step, ...patch } : step)));
  }

  async function trigger() {
    setRunning(true);
    setSteps([
      { label: "Upload demo frame → Ingest", status: "pending" },
      { label: "Vision · Gemini analyzes frame", status: "pending" },
      { label: "Orchestrator · classify + dispatch", status: "pending" },
    ]);

    try {
      // 1 — ingest
      update(0, { status: "running" });
      const frame = await loadDemoFrame();
      const frameBuffer = toArrayBuffer(frame);
      const form = new FormData();
      form.append("venue_id", VENUE);
      form.append("camera_id", "demo-cam");
      form.append("zone_id", "kitchen-main");
      form.append("frame", new Blob([frameBuffer], { type: "image/jpeg" }), "demo.jpg");
      const ingestResp = await fetch(`${INGEST_BASE}/v1/frames`, { method: "POST", body: form });
      if (!ingestResp.ok) throw new Error(`ingest ${ingestResp.status}`);
      update(0, { status: "ok", detail: "frame accepted" });

      // 2 — vision (synchronous for demo)
      update(1, { status: "running" });
      const b64 = typeof window !== "undefined"
        ? await blobToBase64(new Blob([frameBuffer], { type: "image/jpeg" }))
        : "";
      const visResp = await fetch(`${VISION_BASE}/v1/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          venue_id: VENUE,
          camera_id: "demo-cam",
          zone_id: "kitchen-main",
          frame_base64: b64,
          publish: false,
        }),
      });
      if (!visResp.ok) throw new Error(`vision ${visResp.status}`);
      const vis = await visResp.json();
      update(1, {
        status: "ok",
        detail: `${vis.signal.category_hint} · conf ${Math.round(vis.signal.confidence * 100)}% · ${
          vis.used_gemini ? "Gemini" : "fallback"
        }`,
      });

      // 3 — orchestrator
      update(2, { status: "running" });
      const orchResp = await fetch(`${ORCH_BASE}/v1/handle-batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          venue_id: VENUE,
          zone_id: "kitchen-main",
          signals: [vis.signal],
        }),
      });
      if (!orchResp.ok) throw new Error(`orch ${orchResp.status}`);
      const orch = await orchResp.json();
      update(2, {
        status: "ok",
        detail: `${orch.result.incident.incident_id} · ${orch.result.classification.severity} · dispatched=${orch.dispatched}`,
      });
    } catch (err) {
      const last = steps.findIndex((s) => s.status === "running");
      if (last >= 0) update(last, { status: "error", detail: String(err) });
      else setSteps((s) => [...s, { label: "error", status: "error", detail: String(err) }]);
    } finally {
      setRunning(false);
    }
  }

  return (
    <main style={{ padding: 16, maxWidth: 640, margin: "0 auto" }}>
      <div
        style={{
          fontFamily: "var(--font-mono)",
          fontSize: 11,
          letterSpacing: "0.16em",
          color: "var(--c-ink-muted)",
        }}
      >
        AEGIS · DASHBOARD DRILL
      </div>
      <h1 style={{ fontSize: 28, fontWeight: 700, margin: "6px 0 12px" }}>Fire a demo incident</h1>
      <p style={{ color: "var(--c-ink-secondary)", marginTop: 0 }}>
        Sends one synthetic frame end-to-end through Ingest → Vision → Orchestrator. Use
        this during the judge demo to show the 4-second detection-to-dispatch path live.
      </p>

      <button
        onClick={trigger}
        disabled={running}
        style={{
          marginTop: 16,
          background: "#14B8A6",
          color: "#0A0E14",
          border: "none",
          borderRadius: 10,
          padding: "16px 22px",
          fontSize: 16,
          fontWeight: 600,
        }}
      >
        {running ? "Running..." : "Trigger drill"}
      </button>

      <div style={{ marginTop: 24, display: "flex", flexDirection: "column", gap: 8 }}>
        {steps.map((s, i) => (
          <div
            key={i}
            style={{
              padding: 12,
              background: "var(--c-bg-elevated)",
              border: "1px solid var(--c-border)",
              borderRadius: 8,
              display: "flex",
              gap: 10,
              alignItems: "center",
            }}
          >
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: 999,
                background: {
                  pending: "#334155",
                  running: "#F59E0B",
                  ok: "#10B981",
                  error: "#DC2626",
                }[s.status],
              }}
            />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 14 }}>{s.label}</div>
              {s.detail ? (
                <div
                  style={{
                    fontFamily: "JetBrains Mono, monospace",
                    fontSize: 11.5,
                    color: "var(--c-ink-muted)",
                  }}
                >
                  {s.detail}
                </div>
              ) : null}
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 40, borderTop: "1px solid var(--c-border)", paddingTop: 18 }}>
        <Link href="/" style={{ fontSize: 12, fontFamily: "var(--font-mono)" }}>
          ← LIVE BOARD
        </Link>
      </div>
    </main>
  );
}

async function loadDemoFrame(): Promise<Uint8Array> {
  // Prefer the real demo still image checked into /public. The tiny fallback
  // keeps local demos alive even when the asset is unavailable.
  try {
    const resp = await fetch("/demo-frame.jpg");
    if (resp.ok) return new Uint8Array(await resp.arrayBuffer());
  } catch {}
  // Fallback: 67-byte JPEG of a red pixel.
  return new Uint8Array([
    0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46, 0x00, 0x01, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x01, 0x00, 0x00, 0xff, 0xdb, 0x00, 0x43, 0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08,
    0x07, 0x07, 0x07, 0x09, 0x09, 0x08, 0x0a, 0x0c, 0x14, 0x0d, 0x0c, 0x0b, 0x0b, 0x0c, 0x19, 0x12,
    0x13, 0x0f, 0x14, 0x1d, 0x1a, 0x1f, 0x1e, 0x1d, 0x1a, 0x1c, 0x1c, 0x20, 0x24, 0x2e, 0x27, 0x20,
    0xff, 0xd9,
  ]);
}

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const s = (reader.result as string) || "";
      resolve(s.split(",").pop() ?? "");
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function toArrayBuffer(bytes: Uint8Array): ArrayBuffer {
  return bytes.buffer.slice(
    bytes.byteOffset,
    bytes.byteOffset + bytes.byteLength,
  ) as ArrayBuffer;
}
