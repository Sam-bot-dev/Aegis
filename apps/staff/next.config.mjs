// apps/staff/next.config.mjs
/** @type {import('next').NextConfig} */

// Origins the staff PWA is allowed to connect to.
// Cloud Run services land on *.run.app; Firebase App Hosting on *.hosted.app.
// Firebase SDK needs *.googleapis.com (Auth, Firestore REST) and
// *.firebaseio.com / wss://*.firebaseio.com (Firestore realtime listener).
const CSP_CONNECT_SRC = [
  "'self'",
  "https://*.run.app",
  "https://*.hosted.app",
  "https://*.googleapis.com",
  "https://*.firebaseio.com",
  "wss://*.firebaseio.com",
].join(" ");

const securityHeaders = [
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      // Next.js inlines scripts; tighten to nonces in prod once you have a nonce strategy.
      // apis.google.com required for Firebase Auth Google Sign-In (api.js).
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: blob: https:",
      "font-src 'self' data:",
      `connect-src ${CSP_CONNECT_SRC}`,
      "worker-src 'self' blob:",
      // accounts.google.com: OAuth popup; *.firebaseapp.com: Firebase Auth session iframe.
      "frame-src https://accounts.google.com https://*.firebaseapp.com",
      "frame-ancestors 'none'",
    ].join("; "),
  },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "geolocation=(), microphone=(), camera=()",
  },
];

const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@aegis/ui-web"],
  experimental: {
    typedRoutes: false,
  },
  async headers() {
    return [
      {
        // Apply to every route
        source: "/(.*)",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;