# Orchestrator Agent

Top-level agent for the Aegis incident response graph. Runs a ReAct-style
loop: observe perceptual signals, reason, invoke sub-agents as tools,
compose their outputs, act.

**Model:** `gemini-2.5-pro` (complex reasoning; latency secondary)
**Prompt:** `/prompts/orchestrator.md`
**Tools:** `classify_incident`, `predict_cascade`, `medical_triage`,
          `dispatch_responders`, `plan_evacuation`, `compose_comms`,
          `notify_authorities`, `write_audit_entry`,
          `update_firestore_incident_state`

## Phase 1 (shipped)

Not this agent. Phase 1 uses a deterministic Python function in
`services/orchestrator/main.py` so the pipeline runs end-to-end without
ADK.

## Phase 2 (target)

Implement `OrchestratorAgent(Agent)` using Vertex AI ADK. Deploy to Agent
Engine. The Orchestrator service becomes a thin wrapper that streams
perceptual signals into Agent Engine sessions and relays the results.

### Build order for this agent

1. Stub each sub-agent as a Python function that returns a typed
   Pydantic response with hardcoded values
2. Wire those stubs into `OrchestratorAgent` as `Tool.from_fn(...)`
3. Write the eval harness: 10 synthetic scenarios with known
   ground-truth dispatches
4. Replace one stub at a time with a real sub-agent, re-running evals

### Key files (to be added)

```
agents/orchestrator/
├── README.md                ← this file
├── agent.py                 ← OrchestratorAgent class
├── tools.py                 ← tool function signatures
├── tests/
│   ├── test_smoke.py        ← "agent runs end-to-end on canned input"
│   └── scenarios/           ← eval scenarios
└── pyproject.toml
```

See `services/shared/aegis_shared/schemas.py` for the Pydantic models
that agents must accept and return.
