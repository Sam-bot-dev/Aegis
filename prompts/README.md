# Aegis agent prompts

Every agent system prompt lives here as a versioned markdown file. Loaded at
runtime via `aegis_shared.prompts.PromptRegistry` (implemented in Phase 2).
Every invocation records the `prompt_hash` in the audit log so we can trace
a decision back to the exact prompt text used.

## Current prompts

| File                       | Agent                | Model              | Phase |
| -------------------------- | -------------------- | ------------------ | ----- |
| `orchestrator.md`          | Orchestrator         | gemini-2.5-pro     | 2     |
| `vision_classifier.md`     | Vision Classifier    | gemini-2.5-flash   | 2     |
| `cascade_predictor.md`     | Cascade Predictor    | gemini-2.5-pro     | 2 (TODO) |
| `triage_agent.md`          | Triage Agent         | MedGemma           | 2 (TODO) |
| `dispatcher.md`            | Dispatcher Agent     | gemini-2.5-flash   | 2 (TODO) |
| `comms_agent.md`           | Communications       | gemini-2.5-flash   | 2 (TODO) |
| `post_incident_report.md`  | Post-Incident        | gemini-2.5-pro     | 3 (TODO) |

## Rules for changing a prompt

1. Never overwrite — **bump the version** inside the file and in the registry.
2. Every change needs a PR with eval-harness results showing ≥ the previous score.
3. Prompts are part of the audit trail. Deleting a prompt version is not allowed.
