# ADR-0004: Dispatcher uses layered ranking instead of a full optimizer

**Status:** Accepted · 2026-04-24 · Proposer: @ubaid

## Context

Dispatching in Aegis needs to account for skill fit, availability, credential
validity, ETA, language, and workload. A full integer-programming or CSP
solution is attractive in theory, but Phase 1 needed something:

- fast enough for the under-60-second story
- explainable in code review
- resilient when model calls fail

## Decision

The Dispatcher agent will use a layered approach:

1. Hard filters eliminate ineligible responders.
2. A weighted score ranks the remaining candidates.
3. Gemini reranks only the top few candidates for high-severity incidents.
4. The agent emits a primary assignment plus a backup ladder.

This keeps deterministic behavior in the critical path while still allowing AI
judgment where it adds the most value.

## Consequences

### Positive

- Fast and understandable responder selection
- Deterministic fallback when Gemini is unavailable
- Clear place to add richer optimization later without throwing away Phase 1

### Negative / Accepted tradeoffs

- The current approach is not a globally optimal solver
- Tradeoff weights are heuristic and may need venue tuning
- Backup ladder escalation still needs more durable runtime support

### Review trigger

Re-open this ADR if:

- responder selection quality is clearly suboptimal in drills
- venue-specific rules outgrow simple weighted scoring
- we need hard optimization guarantees for large rosters
