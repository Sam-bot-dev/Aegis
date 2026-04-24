# Communications Agent

Generates multilingual guest comms, staff briefings, and authority
incident packets.

**Model:** `gemini-2.5-flash` (speed)
**Tools:** Cloud Translation, Cloud Text-to-Speech, template registry

## Output types

1. **Guest PA announcement** — drafted by agent → Cloud Translation
   (5 languages) → Cloud TTS (neural voice, calm tone) → venue PA API
2. **Guest phone push** (FCM) — one-screen card with route, assembly
   point, accessibility notes
3. **Staff briefing** — short Firestore chat message with key
   instructions, zone assignments
4. **Authority incident packet** — structured JSON-LD (`schema.org/
   EmergencyEvent` + Aegis extensions), signed with the venue's
   Ed25519 key
5. **Next-of-kin SMS** (P2, consented) — MSG91 in India

## Languages at launch

English, Hindi, Gujarati, Tamil, Bengali. Glossary for safety-critical
terms in `/i18n/glossary/` (coming in Phase 2) — `"assembly point"` is
not auto-translated to a mistranslation; it maps to a known phrase.

## Tone rules

- No exclamation points
- No emojis
- No "please" in critical instructions (ambiguous in translation)
- Short sentences, active voice
- Fact first, action second ("Fire in main kitchen. Exit via stairwell B.")

## Phase 1

Not built. Phase 1 shows a hardcoded English announcement in the staff
app.
