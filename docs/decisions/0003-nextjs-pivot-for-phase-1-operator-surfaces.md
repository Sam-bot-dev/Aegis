# ADR-0003: Use Next.js for Phase 1 operator surfaces

**Status:** Accepted · 2026-04-24 · Proposer: @ubaid

## Context

The original blueprint centered Flutter for staff and responder experiences.
That remains attractive long-term, especially for lower-end Android devices,
push, and offline workflows. But for Phase 1 we needed to ship two usable
operator surfaces in under 48 hours:

1. A staff-facing acknowledgment flow
2. A desktop dashboard for the venue control room

Building both in Flutter during the submission window would have slowed
iteration and made web deployment harder.

## Decision

For Phase 1, the staff app and dashboard app will use Next.js 14 with the
Firebase web SDK. Flutter remains the plan for the dedicated responder app in
Phase 2, when offline behavior and device-native affordances matter more.

## Consequences

### Positive

- Faster iteration on web-first judge-demo surfaces
- Easy deployment to Cloud Run or Firebase Hosting
- Shared TypeScript types and UI primitives across both apps

### Negative / Accepted tradeoffs

- The staff experience is not yet a true native mobile app
- Phone OTP auth, push registration, and offline behavior still need follow-up
- We now carry a temporary split strategy: Next.js today, Flutter later

### Review trigger

Re-open this ADR if:

- The web staff surface becomes a blocker for real pilot usage
- Flutter can be reintroduced without slowing the Phase 2 roadmap
- We decide to consolidate all operator surfaces into a single mobile stack
