# ADR-0005: Cascade prediction uses Gemini Pro with heuristic backstop

**Status:** Accepted · 2026-04-24 · Proposer: @ubaid

## Context

Cascade prediction is one of Aegis's novelty points. It needs to answer "what
happens next?" rather than only "what is happening now?" For fire, crowd, and
medical events we want 30/90/300 second forecasts plus preemptive actions.

A purely heuristic model is fast but shallow. A full graph-aware reasoning
stack is more compelling, but it is also heavier and more fragile during
Phase 1.

## Decision

The Cascade agent uses Gemini 2.5 Pro for richer forward-looking predictions,
with a category-specific heuristic fallback when the model is unavailable. The
heuristic path guarantees the dashboard can still show a forecast, even during
credential or latency failures.

## Consequences

### Positive

- Stronger "AI that thinks ahead" story in demos
- Structured predictions that can be shown directly in the incident detail UI
- Safe fallback behavior when the model path fails

### Negative / Accepted tradeoffs

- Pro is slower and more expensive than Flash
- Forecast quality is limited until venue graph context is added
- The prompt still needs extraction into the shared prompt registry

### Review trigger

Re-open this ADR if:

- Gemini Pro latency becomes unacceptable in active incidents
- heuristic outputs routinely outperform the model in drills
- venue map context is ready and changes the prompt/interface shape
