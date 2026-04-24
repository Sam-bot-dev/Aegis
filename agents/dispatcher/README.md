# Dispatcher Agent

Triage-constrained responder dispatcher. **Second of the five novel
contributions** (blueprint §60).

Chooses which responder(s) to page for an incident. Formulated as a
constraint-satisfaction problem with a hybrid approach:

1. Integer LP narrows to top-3 candidates by objective function
2. Gemini re-ranks the top-3 using contextual reasoning about the
   specific patient / scenario

**Model:** `gemini-2.5-flash` (the re-rank step; the LP is pure Python)
**Tools:** `list_available_responders`, `responder_skill_vector`,
          `estimate_eta`, `matching_engine_lookup`

## Problem framing

```
Variables: x_r ∈ {0,1} for each available responder r
Constraints:
  Σ x_r = 1              (primary; multi-dispatch for S1)
  x_r = 0  if skill < threshold
  x_r = 0  if credential expired
  x_r = 0  if off-shift
  x_r = 0  if eta > max_allowed
Objective:
  minimize eta + λ₁ (1 - skill_score) + λ₂ (1 - lang_score) + λ₃ workload
```

## Phase 1

Dispatcher is a no-op: orchestrator publishes a dispatch event with just
a severity and the dispatch service handles it. Assignment to a specific
responder is Phase 2.

## Phase 2 scaffold

```
agents/dispatcher/
├── agent.py           ← DispatcherAgent class
├── optimizer.py       ← PuLP + CBC LP solver
├── reranker.py        ← Gemini contextual re-rank
├── responder_index.py ← Matching Engine wrapper for skill vectors
└── tests/
    ├── test_optimizer.py
    └── test_rerank.py
```

Responder skill vectors live in Vertex AI Matching Engine index
`responders-skills-v1` (dimension 512, built nightly).
