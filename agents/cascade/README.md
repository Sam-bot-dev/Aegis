# Cascade Predictor Agent

**This is one of the five novel technical contributions judges will
grade us on.** See blueprint §59. Do not treat this as a routine sub-agent.

Takes a base classification + venue graph context and predicts incident
trajectory 30s / 90s / 300s out. Output is a probability distribution
over cascade outcomes, plus recommended pre-emptive actions.

**Model:** `gemini-2.5-pro` (needs deep reasoning over graph context)
**Prompt:** `/prompts/cascade_predictor.md` (to write)

## Why this matters

A standard classifier labels the current state. Emergencies are
trajectories. A small kitchen fire that will reach a gas line in 90s is
a fundamentally different incident than a small kitchen fire that
won't. Cascade prediction unlocks *pre-emptive* action — the killer
demo narrative (blueprint §8.2 Indian Wedding Stampede).

## Input

```python
{
    "classification": IncidentClassification,  # the base label
    "venue_subgraph": {...},  # zones adjacent to the affected one
    "zone_occupancy": {...},  # current person counts per zone
    "time_of_day_base_rates": {...},
    "high_risk_attributes": ["gas_line_nearby", "disability_guest_312", ...]
}
```

## Output

```python
{
    "predictions": [
        {"horizon_seconds": 30, "outcome": "contained", "probability": 0.62},
        {"horizon_seconds": 90, "outcome": "vertical_smoke_spread", "probability": 0.21},
        {"horizon_seconds": 300, "outcome": "multi_floor_spread", "probability": 0.09},
    ],
    "recommended_preemptive_actions": [
        {"action": "pre_alert_rooms_above", "trigger_horizon_seconds": 60},
        {"action": "stage_fire_service", "trigger_horizon_seconds": 90},
    ],
    "rationale": "..."
}
```

## Evaluation plan

20 synthetic cascade scenarios with known outcomes. Measure:

- Brier score on the probability predictions
- Pre-emptive action precision (when we recommend it, does the cascade
  actually happen?)
- p95 latency (target < 2s)

Report these numbers in the Phase 3 deck. Judges will ask.

## Not built yet

Cascade prediction is **Phase 2** work. Scaffold only for now.
