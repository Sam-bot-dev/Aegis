# Triage Agent (MedGemma)

Medical triage for MEDICAL-category incidents. Produces acuity level,
likely condition, and pre-hospital instructions from a pre-approved
library.

**Model:** MedGemma (Google's open medical model, via Vertex AI Endpoint)
**Prompt:** `/prompts/triage.md` (to write)
**Tools:** `patient_state`, `medical_kb_retrieve`

## Non-negotiable safety envelope

- MedGemma output is NEVER surfaced directly to a guest or non-clinical
  staff
- Output augments the incident brief sent to a **credentialed
  responder only**
- Pre-hospital instructions come from a **closed library of approved
  phrases** (not free-form model output)
- Every call carries an "advisory, not medical direction" label in the
  audit record

## Output schema

```python
{
    "esi_level": 1..5,             # Emergency Severity Index
    "likely_condition": str,       # from allow-list
    "pre_hospital_actions": [      # each item from approved library
        "position_recovery_pose",
        "loosen_tight_clothing",
        "monitor_breathing"
    ],
    "contraindications": [...],    # "do_not_give_water", etc.
    "confidence": float,
    "advisory": "MedGemma output; not a substitute for clinical judgment."
}
```

## Phase 1

Not built. The orchestrator's Phase 1 flow skips triage entirely — any
MEDICAL classification in Phase 1 defaults to "page the on-call doctor,
no pre-advice."

## Phase 2 build order

1. Deploy MedGemma to a Vertex AI Endpoint
2. Build the approved-phrase library (`data/triage_library.json`)
3. Write prompt that constrains output to the library
4. RAG over a curated medical KB stored in Matching Engine
   `medical-kb-v1`
5. Eval against 30 scenarios with known correct triage
