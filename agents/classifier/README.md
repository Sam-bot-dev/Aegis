# Classifier Agent

Multi-modal fused classifier. Takes a batch of perceptual signals (vision
frame + audio snippet + sensor state) and returns an
`IncidentClassification`.

**Model:** `gemini-2.5-flash` (speed priority; p95 < 1.5s target)
**Prompt:** `/prompts/vision_classifier.md` + a fusion extension
**Tools:** none — single-shot model call

## Output schema

Returns an `IncidentClassification` (see
`aegis_shared.schemas.IncidentClassification`):

```python
{
    "category": "FIRE" | "MEDICAL" | "STAMPEDE" | "VIOLENCE" | "SUSPICIOUS" | "OTHER",
    "sub_type": str | None,
    "severity": "S1" | "S2" | "S3" | "S4",
    "confidence": float,  # 0..1
    "rationale": str,
    "cascade_predictions": []  # filled by Cascade agent
}
```

## Severity rubric

- **S1 (Critical):** active fire with spread risk; cardiac arrest;
  active violence; stampede in progress. Triggers autonomous dispatch
  if venue has opted in.
- **S2 (Urgent):** contained fire; medical emergency not immediately
  life-threatening; pre-cursor to stampede. Paged but operator ack'd.
- **S3 (Monitor):** ambiguous signal; low-confidence classification;
  nuisance with context worth watching. Logged, no paging.
- **S4 (Nuisance):** clear false positive; training feedback only.

## Phase 1 fallback

The deterministic classifier in `services/orchestrator/main.py`
(`_classify_phase1`) covers the demo.

## Phase 2 implementation

Replace with real Gemini call using `aegis_shared.gemini.GeminiClient`:

```python
from aegis_shared.gemini import GeminiClient
from aegis_shared.schemas import IncidentClassification

client = GeminiClient()
classification = await client.generate_structured(
    prompt=build_prompt(signals),
    schema=IncidentClassification,
    model="flash",
    system_instruction=load_prompt("vision_classifier"),
)
```
