"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useAuth, signInWithGoogle, signInWithEmail } from "@aegis/ui-web";

export default function LoginPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [busy, setBusy] = React.useState(false);

  // Already signed in → go straight to the control room
  React.useEffect(() => {
    if (!loading && user) router.replace("/");
  }, [user, loading, router]);

  async function handleGoogle() {
    setError(null);
    setBusy(true);
    try {
      await signInWithGoogle();
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleEmail(e: React.FormEvent) {
    e.preventDefault();
    if (!email || !password) return;
    setError(null);
    setBusy(true);
    try {
      await signInWithEmail(email, password);
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div style={centerStyle}>
        <Spinner />
      </div>
    );
  }

  return (
    <div style={centerStyle}>
      <div style={cardStyle}>
        {/* Logo */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 28 }}>
          <svg width={22} height={30} viewBox="0 0 28 40" fill="none">
            <path d="M4 4H10V2H18V4H24V22C24 30 14 36 14 36C14 36 4 30 4 22V4Z" stroke="#14b8a6" strokeWidth={1.5} />
            <path d="M14 10V28M9 18H19" stroke="#14b8a6" strokeWidth={1.2} opacity={0.55} />
          </svg>
          <div>
            <div style={{ fontSize: 17, fontWeight: 700, letterSpacing: "0.02em" }}>AEGIS</div>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: 9, letterSpacing: "0.14em", color: "var(--c-ink-muted)", textTransform: "uppercase" }}>
              Control Room
            </div>
          </div>
        </div>

        <h1 style={{ fontSize: 22, fontWeight: 600, marginBottom: 6 }}>Sign in</h1>
        <p style={{ fontSize: 13, color: "var(--c-ink-secondary)", marginBottom: 24 }}>
          Operator access · venue dashboard
        </p>

        {/* Google */}
        <button
          onClick={handleGoogle}
          disabled={busy}
          style={googleBtnStyle}
        >
          <GoogleIcon />
          Continue with Google
        </button>

        <div style={dividerStyle}>
          <div style={dividerLineStyle} />
          <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--c-ink-muted)", padding: "0 12px" }}>or</span>
          <div style={dividerLineStyle} />
        </div>

        {/* Email / password */}
        <form onSubmit={handleEmail} style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="operator@venue.com"
            required
            autoComplete="email"
            style={inputStyle}
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
            autoComplete="current-password"
            style={inputStyle}
          />
          <button type="submit" disabled={busy || !email || !password} style={submitBtnStyle}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>

        {error ? (
          <div style={errorStyle}>{error}</div>
        ) : null}

        <p style={{ marginTop: 20, fontSize: 11, color: "var(--c-ink-muted)", textAlign: "center", lineHeight: 1.5 }}>
          Access is restricted to authorised operators.
          <br />Contact your venue admin to request access.
        </p>
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <div
      style={{
        width: 28,
        height: 28,
        border: "2px solid rgba(20,184,166,0.2)",
        borderTop: "2px solid #14b8a6",
        borderRadius: "50%",
        animation: "spin 0.7s linear infinite",
      }}
    />
  );
}

function GoogleIcon() {
  return (
    <svg width={18} height={18} viewBox="0 0 18 18" fill="none">
      <path d="M17.64 9.2a10.34 10.34 0 0 0-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92A8.78 8.78 0 0 0 17.64 9.2z" fill="#4285F4" />
      <path d="M9 18a8.59 8.59 0 0 0 5.96-2.18l-2.92-2.26a5.43 5.43 0 0 1-3.04.86 5.38 5.38 0 0 1-5.06-3.72H.96v2.34A9 9 0 0 0 9 18z" fill="#34A853" />
      <path d="M3.94 10.7A5.43 5.43 0 0 1 3.66 9a5.43 5.43 0 0 1 .28-1.7V4.96H.96A9 9 0 0 0 0 9a9 9 0 0 0 .96 4.04l2.98-2.34z" fill="#FBBC05" />
      <path d="M9 3.58a4.86 4.86 0 0 1 3.44 1.34l2.58-2.58A8.64 8.64 0 0 0 9 0a9 9 0 0 0-8.04 4.96l2.98 2.34A5.38 5.38 0 0 1 9 3.58z" fill="#EA4335" />
    </svg>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────
const centerStyle: React.CSSProperties = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "var(--c-bg-primary)",
  padding: 16,
};

const cardStyle: React.CSSProperties = {
  width: "100%",
  maxWidth: 400,
  background: "var(--c-bg-panel)",
  border: "1px solid rgba(51,65,85,0.7)",
  borderRadius: 20,
  backdropFilter: "blur(16px)",
  boxShadow: "0 8px 40px rgba(2,6,23,0.4)",
  padding: "32px 28px",
};

const googleBtnStyle: React.CSSProperties = {
  width: "100%",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: 10,
  padding: "11px 16px",
  borderRadius: 10,
  fontSize: 13,
  fontWeight: 500,
  border: "1px solid rgba(51,65,85,0.8)",
  background: "rgba(255,255,255,0.04)",
  color: "var(--c-ink-primary)",
  cursor: "pointer",
  fontFamily: "inherit",
};

const dividerStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  margin: "18px 0",
};

const dividerLineStyle: React.CSSProperties = {
  flex: 1,
  height: 1,
  background: "rgba(51,65,85,0.5)",
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid rgba(51,65,85,0.7)",
  background: "rgba(255,255,255,0.03)",
  color: "var(--c-ink-primary)",
  fontSize: 13,
  fontFamily: "inherit",
  outline: "none",
};

const submitBtnStyle: React.CSSProperties = {
  width: "100%",
  padding: "11px 16px",
  borderRadius: 10,
  fontSize: 13,
  fontWeight: 600,
  border: "none",
  background: "#14b8a6",
  color: "#0a0e14",
  cursor: "pointer",
  fontFamily: "inherit",
  marginTop: 4,
};

const errorStyle: React.CSSProperties = {
  marginTop: 14,
  padding: "10px 14px",
  borderRadius: 10,
  background: "rgba(220,38,38,0.10)",
  border: "1px solid rgba(220,38,38,0.35)",
  color: "#dc2626",
  fontSize: 12,
};
