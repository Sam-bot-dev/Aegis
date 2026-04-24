# AEGIS — Master Build Blueprint
### Solution Challenge 2026 · Better Call Coders · v1.0 · April 23, 2026

> *An agentic AI platform that turns any mass gathering — hotel, wedding, religious gathering, conference — into a self-monitoring, self-coordinating emergency response system. Collapses the time from incident to dispatched responder from 15 minutes to under 60 seconds.*

---

## How to read this document

This is the single source of truth for Aegis. It is structured so any engineer on the team can open it, find the exact section they own, and start building without needing to ask clarifying questions. It is written in sequence — each section assumes the previous. If you're short on time, read the Executive Summary (§1), the System Architecture (§11), and your assigned build phase (§84–86), then dive into the specific service section you own.

**Navigation:**
- Part I (§1–6): Vision, identity, SDG mapping, users
- Part II (§7–10): Every feature, user journeys
- Part III (§11–14): Architecture
- Part IV (§15–22): Every Google service integration
- Part V (§23–26): Data model
- Part VI (§27–37): Backend services
- Part VII (§38–42): Frontend apps
- Part VIII (§43–50): Design system
- Part IX (§51–55): Every screen spec
- Part X (§56–60): Novel technical contributions (the innovation moat)
- Part XI (§61–67): Security & privacy
- Part XII (§68–73): Scalability
- Part XIII (§74–77): APIs & routing
- Part XIV (§78–83): Code quality, testing, DevOps
- Part XV (§84–87): Development roadmap
- Part XVI (§88–90): Demo & pitch
- Part XVII (§91–93): Validation & partnerships

---

# PART I — VISION & IDENTITY

## §1. Executive Summary

**Aegis** is a multi-agent AI platform that detects, classifies, and coordinates response to safety incidents in mass-gathering venues in near-real-time. It combines computer vision on CCTV feeds, audio event detection, crowdsourced phone sensors (opt-in), and fixed IoT sensors into a perception layer. A Vertex AI Agent Development Kit (ADK) orchestrator runs a team of specialised agents — Classifier, Triage, Dispatcher, Communications, Evacuation, Authority Reporter — that collapse the time between incident occurrence and coordinated on-ground response.

The product serves four operator types: venue staff, first responders, venue management, and civic authorities. It serves one end beneficiary: the person in danger. Everything in the system is optimised for one metric: **Dispatch Latency (DL)** — the time from the first perceptual signal of an incident to the first qualified responder being on-route with correct triage information. Industry baseline for Indian hotel incidents (2018–2024 case studies) is 12–18 minutes. The Aegis target is **≤ 60 seconds** for 95% of Severity-1 incidents.

Aegis is positioned at the intersection of SDG 3 (Good Health & Well-Being), SDG 11 (Sustainable Cities & Communities), and SDG 16 (Peace, Justice & Strong Institutions). Unlike existing venue safety systems — which are siloed CCTV + siloed PA + siloed PBX + siloed paper log — Aegis is the first coordination layer that unifies perception, decision, dispatch, communication, and audit into a single event-sourced system with a human-in-the-loop safety envelope.

## §2. Project Identity

- **Name:** Aegis (ancient Greek αἰγίς — the shield carried by Athena; symbol of divine protection)
- **Why this name:** Starts with A (alphabetical sort advantage at Grand Finale booth / winner list — documented 2025 Top 3 tactic). Pronounceable in English and Indian languages. Semantically clean — "the aegis of someone" means "under their protection". Domain availability: aegis.care, aegis.safety, tryaegis.com likely available; go register before announcing publicly.
- **Tagline (primary):** *Every second is a life.*
- **Tagline (secondary):** *Sentinel for mass gatherings.*
- **One-line pitch:** *Aegis is an agentic AI platform that detects safety incidents at mass gatherings and coordinates a full response in under 60 seconds.*
- **Elevator pitch (30s):** *Every year, over 2,000 Indians die in venue incidents — hotel fires, wedding stampedes, temple crushes, conference medical emergencies — that were survivable if responders had arrived three minutes earlier. Aegis is the coordination layer between CCTV, staff, and ambulances. Gemini watches every camera, multiple specialised AI agents classify the incident, triage it medically, dispatch the nearest qualified responder, evacuate the right zones, and brief the authorities — all in under 60 seconds. We're starting with Indian hotels and expanding to the ₹500 Cr venue-safety market nobody has yet claimed.*

## §3. Brand & Visual Identity

### §3.1 Logo concept
A shield silhouette formed negatively inside a ripple pattern — the ripple evokes a sound wave (audio detection), the shield evokes protection. Monochrome at small sizes. Color-tinted by incident severity in app contexts (inert blue → amber alert → red critical).

### §3.2 Color system (see §44 for hex values and semantic roles)
- **Brand primary:** Graphite `#0A0E14` (calm, serious, not festive)
- **Brand accent:** Signal Teal `#14B8A6` (positive-connotation action color; used for "system nominal")
- **Alert Amber:** `#F59E0B` (Severity-2 warnings)
- **Critical Red:** `#DC2626` (Severity-1 emergency)
- **Safe Green:** `#10B981` (resolution, success)
- **Neutral ink:** `#F8FAFC` on dark, `#0F172A` on light

### §3.3 Typography
- **Display / brand:** Inter Display (via Google Fonts)
- **UI:** Inter (Google Fonts) — sizes 12/14/16/18/24/32/48
- **Monospace (dashboards, IDs, codes):** JetBrains Mono

### §3.4 Voice & tone
Calm, precise, factual. Aegis never uses exclamation points. Aegis never uses emojis in operator UIs. Aegis never celebrates — a resolved incident is "Resolved: 14:32:07" not "Great job! 🎉". This is deliberate: Aegis is the product in the room when someone has just died, and the tone must be appropriate to that possibility.

## §4. SDG Alignment — Detailed Mapping

The official rubric (§2 of the Strategy Memo) weights "Alignment with Cause" at 25%. Teams that map to three SDGs with specific *target numbers* (not just SDG numbers) score meaningfully higher than teams that name one SDG vaguely. Every feature must have a target-level justification. Here is the complete mapping Aegis will use in its deck:

### §4.1 SDG 3 — Good Health and Well-Being
- **Target 3.6** — *By 2030, halve the number of global deaths and injuries from road traffic accidents.* → Extended to venue-related preventable mortality. Aegis's primary metric (Dispatch Latency) directly compresses the window between trauma and first responder, the single largest variable in survivability for cardiac arrest, anaphylaxis, smoke inhalation, and crush injury.
- **Target 3.d** — *Strengthen the capacity of all countries, in particular developing countries, for early warning, risk reduction and management of national and global health risks.* → Aegis provides early warning infrastructure for mass-gathering health events.

### §4.2 SDG 11 — Sustainable Cities and Communities
- **Target 11.5** — *By 2030, significantly reduce the number of deaths and the number of people affected... by disasters, including water-related disasters, with a focus on protecting the poor and people in vulnerable situations.* → Indian mass gatherings (religious gatherings, low-cost wedding venues, local conferences) disproportionately kill poorer attendees because upmarket venues already have private security. Aegis scales safety to the mid-market.
- **Target 11.7** — *By 2030, provide universal access to safe, inclusive and accessible, green and public spaces, in particular for women, children, older persons and persons with disabilities.* → Aegis's evacuation agent explicitly routes for disability-accessible paths and has children-in-crowd detection.
- **Target 11.b** — *...substantially increase the number of cities and human settlements adopting and implementing integrated policies and plans towards... resilience to disasters, and develop and implement, in line with the Sendai Framework for Disaster Risk Reduction 2015–2030, holistic disaster risk management at all levels.* → Aegis's post-incident report schema is explicitly aligned with the Sendai Framework data requirements.

### §4.3 SDG 16 — Peace, Justice and Strong Institutions
- **Target 16.6** — *Develop effective, accountable and transparent institutions at all levels.* → Every action Aegis takes is logged to an immutable audit trail (BigQuery append-only table with row-level hashing). Authorities, insurers, and legal reviewers can trace every decision.
- **Target 16.10** — *Ensure public access to information and protect fundamental freedoms...* → Guest communications are multi-lingual, accessible (screen-reader, high-contrast), and consent-gated (no guest is surveilled without opt-in to the venue's posted safety notice).

### §4.4 Additional touched SDGs (mention briefly, don't lead with)
- **SDG 5 (Gender Equality)** — Aegis has a dedicated harassment-detection sub-classifier (audio cues, behavioral signals). This is an important differentiator for the Indian women-safety narrative that resonates with judges who remember Saheli (2024 People's Choice winner).
- **SDG 9 (Industry, Innovation & Infrastructure)** — Agentic AI for public-safety infrastructure.
- **SDG 17 (Partnerships)** — Open data pipeline to civic authorities; designed for public-private partnership with state disaster management agencies.

## §5. User Personas

### §5.1 Priya — Hotel Duty Manager (primary operator)
34, works the night shift at a 200-room 4-star hotel in Ahmedabad. Phone is a ₹14,000 Android. Hindi-first, comfortable in English. Has seen two real incidents in 8 years (one kitchen fire, one guest heart attack). Her pain: in both incidents, she wasted 4+ minutes figuring out who to call in what order. Aegis collapses that to zero — her phone buzzes, the incident is already classified, the ambulance is already dispatched, her job is to execute the last-mile (guide the responders, manage evacuation, reassure the guests).

### §5.2 Dr. Kavya — On-Call Hotel Doctor / Responder
42, empanelled with three hotels in the area. Gets calls when there's a medical emergency. Pain point: she arrives without knowing patient vitals, medical history, or even which floor. Aegis pre-briefs her en route with MedGemma-generated triage summary and opens the door directly to the patient with indoor navigation.

### §5.3 Arjun — Local Fire Service Dispatcher
55, sits in a control room with an old PC and a walkie-talkie. Pain point: incoming calls are chaotic and location-vague. Aegis pushes him a structured incident packet (GeoJSON location, incident type, severity, crowd density, access routes, nearest hydrant) the moment an incident is classified — before anyone on-scene even calls him.

### §5.4 Ananya — Corporate Hotel Group Ops Head (enterprise buyer)
38, oversees safety compliance across 15 Taj properties. She's the one who signs the contract. Pain point: HRACC audits, insurance premiums, board-level safety reporting. Aegis gives her a unified dashboard, regulator-ready reports, and insurance premium reductions (10-20% typical for properties with documented <60s dispatch capability).

### §5.5 Rohan — Guest (end beneficiary)
27, checked into room 412 for a work trip. He will never see the Aegis staff app. He may interact with Aegis only through: (a) a PA announcement Gemini generated in his preferred language, (b) a web-based evacuation instruction pushed to his phone if he scans the room QR code, (c) indirectly, through his life being saved when the duty manager responds in 45 seconds instead of 15 minutes.

### §5.6 Meena — Wedding Planner (expansion persona)
31, plans ₹50L–₹5Cr weddings in Ahmedabad. Her pain: liability. Aegis is sold to her as "incident insurance" — if anything goes wrong, there's an immutable audit log showing she followed every protocol.

## §6. Success Metrics

Every feature should be justifiable against these five metrics. If a proposed feature doesn't move one of these, don't build it.

1. **Dispatch Latency (DL):** Time from first perceptual signal to responder en-route with correct brief. Target: p95 ≤ 60s.
2. **False Positive Rate (FPR):** Incidents classified as Severity-1 that turn out to be non-events. Target: ≤ 5 per venue per month (1 per week tolerable; more is an operator-fatigue crisis).
3. **False Negative Rate (FNR):** Real incidents missed by the system. Target: ≤ 0.5% (measured on retrospective review of incident logs).
4. **Staff Actioned Rate (SAR):** % of dispatches where the assigned staff member acknowledged within 15s. Target: ≥ 95%.
5. **Time to Resolution (TTR):** End-to-end time from incident detection to "Resolved" status. Target: median ≤ 12 minutes for medical, ≤ 25 minutes for fire, ≤ 6 minutes for security.

Two product-level metrics judges will want to see in the deck:
- **Lives-years protected:** Based on actuarial tables × venue occupancy × Aegis deployments. Use this in the pitch.
- **Audit trail completeness:** % of dispatched incidents with a complete Sendai-compliant report within 48h of resolution. Target: 100%.

---

# PART II — PRODUCT SPECIFICATION

## §7. Feature Inventory (complete)

Organised by capability domain. Every feature has a priority: **P0** = must ship in Phase 1 (April 24), **P1** = must ship in Phase 2 (Product Vault), **P2** = must ship in Phase 3 (Grand Finale), **P3** = post-hackathon / stretch.

### §7.1 Perception (sensing the world)
| # | Feature | Priority |
|---|---|---|
| 1.1 | CCTV video ingestion (RTSP pull) | P0 |
| 1.2 | CCTV video ingestion (WebRTC push for BYO-feed demos) | P0 |
| 1.3 | Frame-sampled Gemini Vision analysis (1 fps baseline, adaptive up to 5 fps on suspicion) | P0 |
| 1.4 | Audio stream ingestion + Gemini Audio event detection (scream, glass break, gunshot, smoke alarm, crash) | P1 |
| 1.5 | Fixed IoT sensor integration (smoke, heat, CO, door-state) via MQTT | P1 |
| 1.6 | Guest-phone sensor fusion (accelerometer, mic, camera — opt-in via QR) | P2 |
| 1.7 | Venue-map-aware spatial grouping of signals (co-locate evidence from nearby sensors) | P1 |
| 1.8 | Multi-camera same-event deduplication | P1 |
| 1.9 | Privacy-preserving frame processing (face blur before any human review) | P0 |
| 1.10 | Low-light enhancement (for after-hours lobby cams) | P2 |

### §7.2 Classification & Reasoning
| # | Feature | Priority |
|---|---|---|
| 2.1 | Incident Classifier Agent (fire / medical / stampede risk / violence / suspicious / false) | P0 |
| 2.2 | Severity scoring (S1 critical / S2 urgent / S3 monitor / S4 nuisance) | P0 |
| 2.3 | Cascade-aware risk prediction (§56 — novel contribution) | P1 |
| 2.4 | Confidence-scored output with reasoning trace (for audit) | P0 |
| 2.5 | Multi-signal fusion (vision + audio + sensor in one Gemini reasoning call) | P1 |
| 2.6 | False-positive learning loop (operator "that wasn't an incident" feedback) | P1 |
| 2.7 | Venue-specific calibration (same-classifier behaves differently in a temple vs. a boardroom) | P2 |

### §7.3 Triage (medical decisioning)
| # | Feature | Priority |
|---|---|---|
| 3.1 | Triage Agent built on MedGemma (acuity level, likely condition, pre-hospital instructions) | P1 |
| 3.2 | ESI (Emergency Severity Index) 1–5 mapping | P1 |
| 3.3 | Responder-skill matching (cardiac event → cardiology-trained responder preferentially) | P1 |
| 3.4 | Patient vitals capture from responder app (BP, HR, SpO2 input) | P2 |
| 3.5 | Pre-hospital instruction push to staff ("If conscious, position in recovery pose; do not give water") | P1 |

### §7.4 Dispatch
| # | Feature | Priority |
|---|---|---|
| 4.1 | Dispatcher Agent (constraint-satisfaction over responders: nearest + qualified + available + language-match) | P0 |
| 4.2 | Staff device push notification with incident brief | P0 |
| 4.3 | Acknowledge / Accept / Decline flow with 15s timeout → auto-escalate | P0 |
| 4.4 | External responder dispatch (108 ambulance, fire service) via structured incident packet | P1 |
| 4.5 | Live responder ETA + real-time position on map | P1 |
| 4.6 | Responder escalation ladder (staff → on-call doctor → 108 → hospital) | P1 |
| 4.7 | Handoff protocol from staff to arriving responder (code word + QR scan) | P2 |

### §7.5 Evacuation
| # | Feature | Priority |
|---|---|---|
| 5.1 | Zone-aware evacuation route generation (Google Maps Routes + indoor graph) | P1 |
| 5.2 | Crowd-density aware routing (§60 — avoid routing into a choke point) | P1 |
| 5.3 | Disability-accessible path preference | P1 |
| 5.4 | Zone closure directives (this staircase is on fire — don't route anyone here) | P1 |
| 5.5 | Multilingual guest instructions (5 languages at launch: English, Hindi, Gujarati, Tamil, Bengali) | P1 |
| 5.6 | Staff zone-clearance checklist with progress tracking | P1 |
| 5.7 | Assembly point confirmation (head-count via staff or guest check-in) | P2 |

### §7.6 Communications
| # | Feature | Priority |
|---|---|---|
| 6.1 | Multi-language guest PA announcement (Gemini generates → Cloud TTS → venue PA API) | P1 |
| 6.2 | Guest phone push (FCM) with localized evacuation card | P2 |
| 6.3 | Staff group chat (Firestore-backed, E2E via Firebase Auth custom tokens) | P1 |
| 6.4 | Radio-style voice broadcast to staff (walkie-talkie PTT over WebRTC) | P2 |
| 6.5 | Authority incident packet (structured JSON → webhook or fax fallback) | P1 |
| 6.6 | Next-of-kin notification (consented, staff-confirmed, multi-lingual) | P2 |
| 6.7 | Media/press holding statement auto-draft (for venue PR team) | P3 |

### §7.7 Venue Management
| # | Feature | Priority |
|---|---|---|
| 7.1 | Venue onboarding wizard (upload floor plan, map cameras, define zones) | P1 |
| 7.2 | Floor plan annotation tool (exits, hydrants, AEDs, assembly points) | P1 |
| 7.3 | Staff roster + credentialing + shift scheduling | P1 |
| 7.4 | Sensor calibration UI (test fire via hairdryer near smoke detector, verify end-to-end) | P2 |
| 7.5 | Drill mode (simulate incident without firing real dispatch) | P1 |
| 7.6 | Venue-specific classifier threshold tuning | P2 |

### §7.8 Authority & Compliance
| # | Feature | Priority |
|---|---|---|
| 8.1 | Real-time authority webhook (fire service, ambulance, police) | P1 |
| 8.2 | Sendai-compliant post-incident report auto-generation | P1 |
| 8.3 | HRACC / NDMA regulatory report export (PDF) | P2 |
| 8.4 | Insurance claim evidence packet (timestamped video, audit log) | P2 |
| 8.5 | Legal hold + chain-of-custody export | P3 |

### §7.9 Analytics & Learning
| # | Feature | Priority |
|---|---|---|
| 9.1 | Venue incident dashboard (trends, Dispatch Latency, FPR, SAR) | P1 |
| 9.2 | Predictive risk heatmap (which zones trend toward incidents at which times) | P2 |
| 9.3 | Post-incident learning loop (every incident → fine-tune example) | P2 |
| 9.4 | Cross-venue insights (anonymised) — "peer venues saw 40% drop in DL after X" | P3 |
| 9.5 | Fairness dashboard (ensure FPR does not vary across demographic camera zones — novel responsible-AI point) | P2 |

### §7.10 Security, Privacy, Accessibility
| # | Feature | Priority |
|---|---|---|
| 10.1 | Firebase Auth + Identity Platform for RBAC | P0 |
| 10.2 | Firebase App Check (prevent API abuse from non-Aegis clients) | P1 |
| 10.3 | Cloud DLP on every frame before human review (mask IDs, credit cards, license plates) | P1 |
| 10.4 | On-device feature extraction for guest-phone mode (no raw video leaves the phone) | P2 |
| 10.5 | Immutable audit log with row-level hashing | P1 |
| 10.6 | Consent management (guest opt-in/out, granular) | P2 |
| 10.7 | WCAG 2.1 AA across all surfaces | P1 |
| 10.8 | Offline-first staff app (Firebase offline persistence + conflict-resolution queue) | P1 |
| 10.9 | Multi-lingual UI (5 languages at launch, 20+ in roadmap) | P1 |
| 10.10 | Operator fatigue protection (max X alerts per hour; auto-quiet after Y) | P2 |

### §7.11 Human-in-the-loop safety
| # | Feature | Priority |
|---|---|---|
| 11.1 | Every dispatch is operator-confirmable within 15s before automation (mode: "co-pilot") | P0 |
| 11.2 | Full "autonomous" mode disabled by default; venue opt-in | P1 |
| 11.3 | Kill-switch on venue dashboard (pause Aegis without logging out) | P1 |
| 11.4 | Explainable-AI view: why did Aegis classify this as a fire? | P1 |

## §8. User Journeys

### §8.1 Journey A — Hotel Kitchen Fire (Primary demo scenario)

T+0:00 — Deep fryer catches fire in the main kitchen. Kitchen staff grabs extinguisher but is a novice.
T+0:03 — CCTV camera #K-12 frames sampled to Gemini Vision. Prior 1 fps baseline; detection of flame + smoke signature pushes sampling to 5 fps.
T+0:05 — Gemini Vision returns {category: fire, confidence: 0.91, sub-type: cooking_fire, flame_spread_rate: moderate}. Co-occurring signals: smoke detector K-S-07 just fired, audio agent detected fire-alarm siren.
T+0:07 — Incident Classifier fuses signals: {incident_id: INC-7741, category: FIRE, sub: KITCHEN, severity: S2 (not yet S1 because contained), confidence: 0.94}.
T+0:08 — Cascade Predictor runs: "If not extinguished in 90s, transitions to S1 (gas line risk); 4 guest rooms directly above — vertical smoke path; one disability-tagged guest in 312."
T+0:10 — Orchestrator dispatches in parallel:
  - Dispatcher Agent: pages Priya (duty manager, nearest), John (fire warden, on floor 1), and external fire service via structured webhook.
  - Evacuation Agent: pre-computes routes if cascade triggers (does not evacuate yet — false alarm tolerance).
  - Comms Agent: prepares multi-language PA script, holds for operator approval.
T+0:12 — Priya's phone buzzes with Severity-2 card: location pin, incident type, 90-second cascade warning, one-tap Accept / Escalate / Dismiss.
T+0:14 — Priya taps Accept. Staff chat auto-opens with John. Authority webhook confirmed delivered.
T+0:28 — Kitchen staff deploys extinguisher. CCTV sees flame reducing.
T+0:45 — Fire still suppressed; classifier downgrades to S3.
T+1:10 — Flame fully out. Priya marks "Verify Before Close". Drone or walk-through camera confirms. Incident resolved at T+3:40.
T+24h — Auto-generated post-incident report + learning example added to tuning dataset.

**Dispatch Latency on this example: 12 seconds** (from first perceptual signal at T+0:03 to responder en-route at T+0:14, wall-clock from incident start: 14 seconds).

### §8.2 Journey B — Indian Wedding Stampede Risk (Core differentiator)
At a 1,500-guest wedding, a DJ announces a surprise fireworks moment. Crowd surges toward the stage. Cascade Predictor identifies exponentially-rising crowd density in the main hall + single-exit geometry. Triggers S2 pre-emptive alert: the DJ gets a quiet screen-flash to deploy "hold" (pre-coordinated in venue setup), ushers are routed to open secondary exits proactively. No incident occurs. Post-event: venue dashboard shows "1 prevented near-event" with the cascade trace. **This is the killer demo** — Aegis prevented a non-event, and the audit log proves the prevention.

### §8.3 Journey C — Guest Medical Emergency (Night)
Guest in room 412 suffers cardiac event at 2:47 AM. Hits the in-room SOS button (Aegis-enabled BLE button on the bedside) or yells "help" (room mic with on-device wake-word). Triage Agent (MedGemma) interviews him in Hindi over the in-room speaker: "Can you describe what hurts? Raise the volume if you are short of breath." Response detected. Severity-1. Dr. Kavya paged with full context + floor plan + door code. Meanwhile, staff is dispatched to prop open room, clear corridor, ensure elevator is held on Level 4 for the ambulance team.

### §8.4 Journey D — Religious Gathering Crowd Crush (Expansion scenario; shown in deck)
Temple festival, 8,000 attendees. Aegis (installed by trust's CSR partner) runs density analytics across 40 cameras. An informal narrow stairway starts to congest. Cascade Predictor flags it 40 seconds before any crush. Volunteers are rerouted to direct a one-way flow; a loudspeaker announcement in local language asks the crowd to pause for 60 seconds. Density relaxes. This is also shown in the deck — not built in the MVP, but architected for.

## §9. Core Use Case Flows (state machines)

### §9.1 Incident lifecycle
```
DETECTED → CLASSIFIED → DISPATCHED → ACKNOWLEDGED → EN_ROUTE → ON_SCENE → TRIAGED → RESOLVING → VERIFIED → CLOSED
                 ↓                                                                               ↑
             DISMISSED ─────────────────────────────────────────────────────────────────────────┘
                 ↓
             LEARNING_EXAMPLE_STORED
```

Every transition emits an event to Cloud Pub/Sub topic `incident-events` with the schema in §76.1. Audit log appends a row. UI polls or subscribes via Firestore real-time listener.

### §9.2 Responder engagement state
```
AVAILABLE → PAGED → ACKNOWLEDGED → EN_ROUTE → ARRIVED → ACTIVE → HANDED_OFF → AVAILABLE
                        ↓                         ↓
                   TIMEOUT_AUTO_ESCALATED    DECLINED_AUTO_ESCALATED
```

### §9.3 Zone status during incident
```
CLEAR → WATCHING → AFFECTED → EVACUATING → EVACUATED → ALL_CLEAR_PENDING → CLEAR
                        ↓
                   UNSAFE (no re-entry; authority to clear)
```

## §10. Admin & Operational Flows
Detailed in §41 (Venue Dashboard screens) and §42 (Authority Console screens). Highlights:
- Venue onboarding (15-minute guided wizard)
- Staff onboarding (QR → mobile app → credentialing)
- Drill mode (venue GM can fire "simulated incident" — all agents run, no external webhooks fire, shows full dispatch traces for training)
- Monthly compliance report generation (one click)

---

# PART III — SYSTEM ARCHITECTURE

## §11. High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            EDGE / VENUE PREMISES                                  │
│  CCTV cams · IoT sensors · Staff phones · Guest phones (opt-in) · PA speakers    │
│                                                                                   │
│   [Aegis Edge Gateway]  ← optional; runs on-prem for low-latency + offline       │
│    - RTSP relay  - Frame sampler  - Audio pre-processor  - Local buffer          │
└──────────────────────────┬────────────────────────────────────────────────────────┘
                           │ TLS 1.3 / mTLS  /  HLS for video  /  MQTT for sensors
                           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         GOOGLE CLOUD — INGESTION LAYER                            │
│                                                                                   │
│   [Cloud Run: Ingest API]  [Cloud IoT Core-equiv: Pub/Sub MQTT]  [Cloud Storage] │
│   - Auth via App Check      - Sensor telemetry                    - Raw frames   │
│   - Rate limiting           - Sensor events                       - Audio blobs   │
│     (Apigee / Cloud LB)                                           - Retention 30d │
└──────────────────────────┬────────────────────────────────────────────────────────┘
                           │ Pub/Sub → event bus
                           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         PERCEPTION LAYER (Cloud Run services)                     │
│                                                                                   │
│  [Vision Service]         [Audio Service]        [Sensor Fusion Service]         │
│  - Frame sampling          - Audio event detect  - Co-locate by venue graph      │
│  - Gemini 2.5 Pro / Flash  - Gemini Audio        - Deduplicate multi-camera      │
│  - DLP redaction pre-call  - Whisper fallback    - Emit perceptual_signals       │
│                                                                                   │
└──────────────────────────┬────────────────────────────────────────────────────────┘
                           │ Pub/Sub topic: perceptual_signals
                           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER (Vertex AI Agent Engine / ADK)             │
│                                                                                   │
│         ┌──────────────────── ORCHESTRATOR AGENT ────────────────────┐            │
│         │  State: incident → sub-agents → resolution                  │            │
│         │  Tool-use loop  ·  Failure handling  ·  Audit emission      │            │
│         └───┬────────────┬─────────────┬────────────┬────────────┬───┘            │
│             ▼            ▼             ▼            ▼            ▼                 │
│       [Classifier]  [Triage-Med-   [Dispatcher]  [Evacuation]  [Comms]           │
│       [Cascade       Gemma]         [Authority                  [Report]         │
│        Predictor]                    Reporter]                                   │
└──────────────────────────┬────────────────────────────────────────────────────────┘
                           │ Pub/Sub: incident_events, dispatch_events, etc.
                           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    ACTION LAYER (Cloud Run microservices)                         │
│                                                                                   │
│  [Dispatch Svc]   [Comm Svc]          [Map/Routing Svc]    [Authority Svc]       │
│  - Paging         - FCM / PA / Voice  - Google Maps        - Webhook dispatch    │
│  - Staff chat     - i18n via Translate- Indoor graph       - Incident packet     │
│  - Handoff        - TTS for PA         - Crowd density     - Signed/attested     │
│                                                                                   │
└──────────────────────────┬────────────────────────────────────────────────────────┘
                           │ Firestore / BigQuery / Cloud Storage
                           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                     DATA + STATE + AUDIT LAYER                                    │
│                                                                                   │
│   [Firestore]        [BigQuery]           [Cloud Storage]      [Vertex Matching  │
│   - Live state       - Audit (append)     - Video evidence      Engine]           │
│   - UI subscribers   - Analytics           - Reports            - Responder skill │
│   - Low latency R/W  - Partitioned         - Floor plans          vectors         │
│                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER (clients)                                    │
│                                                                                   │
│  [Staff Flutter]  [Responder Flutter]  [Guest PWA]  [Venue Web]  [Authority Web] │
│  Firebase SDK   · Firebase SDK       · Firebase SDK · Next.js   · Next.js        │
│  FCM, Firestore · FCM, Firestore     · PWA, Maps    · Firestore · Firestore      │
│  Offline first  · Offline first      · Light         · Admin     · Read + export │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## §12. Agent Architecture (Vertex AI ADK)

Agents are built with the Vertex AI Agent Development Kit. The orchestrator is a top-level agent that runs a ReAct-style loop: observe perceptual signals, reason about what is happening, invoke sub-agents as tools, compose their outputs, and act.

### §12.1 Agent catalog

| Agent | Model backbone | Role | Tools / Sub-agents it calls |
|---|---|---|---|
| Orchestrator | Gemini 2.5 Pro | Top-level incident lifecycle | All sub-agents, state store, audit emitter |
| Incident Classifier | Gemini 2.5 Flash (speed priority) | Multi-modal fused classification | Vision Service, Audio Service, Sensor Fusion Service |
| Cascade Predictor | Gemini 2.5 Pro | Predict incident trajectory 30–300s out | Venue graph, historical incident store |
| Triage Agent | MedGemma | Medical acuity + pre-hospital guidance | Patient-state tool, medical knowledge base (Vertex AI Search over curated corpus) |
| Dispatcher Agent | Gemini 2.5 Flash | Constraint-satisfaction responder selection | Responder registry, geolocation tool, availability tool, Matching Engine for skill vectors |
| Evacuation Agent | Gemini 2.5 Pro + graph solver | Compute safe routes | Maps Routes API, indoor graph, crowd-density snapshot |
| Communications Agent | Gemini 2.5 Flash | Draft multi-lingual guest + authority comms | Cloud Translation, Cloud TTS, template store |
| Authority Reporter | Gemini 2.5 Flash | Compose structured incident packet | Report schema validator, signing service |
| Post-Incident Report Agent | Gemini 2.5 Pro | Compose Sendai-format retrospective | Audit log (BigQuery), video evidence, fairness analyzer |
| Learning Loop Agent | (batch job, Vertex AI Pipelines) | Convert resolved incidents into tuning examples | Cloud Storage, Vertex AI Training |

### §12.2 ADK implementation pattern (pseudocode)

```python
# orchestrator.py — illustrative structure
from vertexai.agents import Agent, Tool
from aegis.agents import (ClassifierAgent, CascadeAgent, TriageAgent,
                          DispatcherAgent, EvacuationAgent, CommsAgent,
                          AuthorityAgent)

class OrchestratorAgent(Agent):
    model = "gemini-2.5-pro"
    system_prompt = AEGIS_ORCH_SYSTEM_PROMPT  # see §12.3
    tools = [
        ClassifierAgent.as_tool(name="classify_incident"),
        CascadeAgent.as_tool(name="predict_cascade"),
        TriageAgent.as_tool(name="medical_triage"),
        DispatcherAgent.as_tool(name="dispatch_responders"),
        EvacuationAgent.as_tool(name="plan_evacuation"),
        CommsAgent.as_tool(name="compose_comms"),
        AuthorityAgent.as_tool(name="notify_authorities"),
        Tool.from_fn(write_audit_entry),
        Tool.from_fn(update_firestore_incident_state),
    ]

    async def handle_signal_batch(self, batch: SignalBatch) -> IncidentRun:
        # 1. Classify
        classification = await self.invoke_tool("classify_incident", batch)
        if classification.severity == "S4_NUISANCE":
            self.log_dismissed(batch, classification); return
        # 2. Predict cascade
        cascade = await self.invoke_tool("predict_cascade",
                                         classification, batch.venue_graph)
        # 3. Parallel branches
        tasks = []
        if classification.category == "MEDICAL":
            tasks.append(self.invoke_tool("medical_triage", classification))
        tasks.append(self.invoke_tool("dispatch_responders", classification, cascade))
        tasks.append(self.invoke_tool("compose_comms", classification, cascade))
        if classification.severity in ("S1", "S2"):
            tasks.append(self.invoke_tool("plan_evacuation", classification, cascade))
            tasks.append(self.invoke_tool("notify_authorities", classification))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # 4. State, audit, human-in-the-loop gates
        await self.update_firestore_incident_state(...)
        await self.write_audit_entry(...)
        return self.compose_run(classification, cascade, results)
```

### §12.3 Orchestrator system prompt (excerpt — full prompt in `/prompts/orchestrator.md`)

```
You are Aegis, the orchestration agent for an emergency-response coordination
system deployed at a mass-gathering venue. Your job is to reason over a batch
of perceptual signals and coordinate sub-agents to detect, classify, and
respond to safety incidents.

Non-negotiable rules:
1. You operate under a human-in-the-loop default. Actions with external side
   effects (dispatching 108 ambulance, triggering PA announcement) MUST be
   gated on a human acknowledge within 15 seconds UNLESS severity=S1 and
   the venue has opted into autonomous mode.
2. You NEVER decide medical treatment. You invoke the Triage Agent, and the
   Triage Agent invokes MedGemma. You NEVER prescribe medication or override
   a certified responder.
3. Every reasoning step emits an audit entry with: timestamp, input hash,
   output hash, model version, confidence, and a human-readable explanation.
4. If a sub-agent returns an error, you NEVER fail silently. You either:
   (a) retry with exponential backoff up to 3 attempts, or
   (b) escalate to human operator with error context.
5. Privacy: before invoking any tool that logs guest imagery, confirm DLP
   has redacted identifying features. If redaction fails, HALT that branch.
6. Fairness: if the same incident category would be classified differently
   in zone A vs zone B based on demographic camera coverage, flag for review.
...
```

### §12.4 Sub-agent contracts

Each sub-agent has a strict Pydantic schema for input and output. Example for the Dispatcher:

```python
class DispatcherInput(BaseModel):
    incident_id: str
    category: Literal["FIRE", "MEDICAL", "STAMPEDE", "VIOLENCE", "OTHER"]
    severity: Literal["S1", "S2", "S3", "S4"]
    location: GeoPoint
    zone_id: str
    required_skills: list[ResponderSkill]
    language_preferences: list[ISO639Code]
    patient_acuity: Optional[ESILevel]
    cascade_horizon_seconds: int

class DispatcherOutput(BaseModel):
    incident_id: str
    dispatched_responders: list[DispatchEntry]
    external_services_notified: list[ExternalServiceNotification]
    backup_ladder: list[ResponderRef]  # if primary declines
    rationale: str  # human-readable, for audit + explainable AI
    confidence: float
```

## §13. Data Flow

### §13.1 Happy-path incident flow
1. Camera → RTSP → Edge Gateway → frame-sampled → Cloud Storage (30d retention, redacted copy) + Pub/Sub `raw_frames`
2. Vision Service consumes `raw_frames` → Gemini 2.5 Flash → emits `perceptual_signals`
3. Sensor Fusion Service correlates with sensors from `sensor_events` → emits `fused_signals`
4. Orchestrator (triggered on new fused_signal) → runs agent graph → emits `incident_events` and `dispatch_events`
5. Dispatch Svc → FCM to staff + webhook to authorities + chat + voice → emits `action_events`
6. All events land in BigQuery via Pub/Sub → BigQuery sink (append-only, hashed)
7. Firestore holds live state (for UI reactivity), BigQuery holds the forever record

### §13.2 Backpressure strategy
- Vision Service has per-camera concurrency cap (default 1 in-flight Gemini call per cam)
- On backpressure, downshift sampling rate (5 fps → 2 fps → 1 fps → 0.5 fps) and defer non-S1 cameras
- Pub/Sub with ordering keys per `venue_id` to prevent out-of-order event processing within a venue
- Dead-letter topic `incident-dlq` for unprocessable events; Cloud Monitoring alert on DLQ depth > 0

### §13.3 Latency budget (p95 target: 4 seconds detection → dispatch, 10 seconds to responder phone)
| Hop | Budget |
|---|---|
| Frame capture → edge sample | 0.5s |
| Edge → Cloud ingest | 0.3s |
| Vision Service invoke → Gemini response | 1.2s (Flash) |
| Fusion + classification | 0.8s |
| Orchestrator agent loop | 1.0s |
| Pub/Sub → Dispatch Svc → FCM delivery | 0.7s |
| **Total wall-clock** | **4.5s** (target), **10s** (p99) |

## §14. Event-Driven Architecture

All inter-service communication goes through Cloud Pub/Sub (never HTTP service-to-service, except where explicitly sync like the Orchestrator → Agent Engine). This buys: backpressure handling, retry, ordering keys, DLQ, fan-out, replay for testing.

Topic list (production):

| Topic | Producer | Consumer(s) | Ordering key |
|---|---|---|---|
| `raw_frames` | Edge Gateway / Ingest API | Vision Service | `venue_id:camera_id` |
| `audio_chunks` | Edge Gateway | Audio Service | `venue_id:mic_id` |
| `sensor_events` | IoT sensors (MQTT bridge) | Sensor Fusion Svc | `venue_id:sensor_id` |
| `perceptual_signals` | Vision/Audio/Fusion | Orchestrator | `venue_id` |
| `incident_events` | Orchestrator | Dispatch Svc, Comm Svc, Audit sink, Firestore sync | `venue_id:incident_id` |
| `dispatch_events` | Dispatch Svc | Staff app (via FCM), Responder app | `venue_id:incident_id` |
| `evacuation_events` | Evacuation Agent | Comm Svc, UI broadcast | `venue_id:incident_id` |
| `authority_events` | Authority Agent | Authority webhook, Audit | `venue_id:incident_id` |
| `audit_events` | All services | BigQuery sink | `venue_id:incident_id` |
| `learning_examples` | Post-Incident Agent | Vertex AI Pipelines | `venue_id` |

---

# PART IV — GOOGLE CLOUD INTEGRATION (EVERY SERVICE)

Every service is listed with: (a) the purpose it serves in Aegis, (b) exactly where it integrates, (c) how it's integrated with code patterns, (d) billing considerations, (e) failure-mode design.

## §15. AI Services

### §15.1 Gemini 2.5 Pro
- **Purpose:** Deep reasoning — Orchestrator top-level, Cascade Predictor, Evacuation Agent, Post-Incident Report Agent.
- **Where integrated:** Vertex AI SDK, accessed from Cloud Run services and from the Agent Engine.
- **How:** `from vertexai.generative_models import GenerativeModel; model = GenerativeModel("gemini-2.5-pro")`. All calls go through a `GeminiClient` wrapper (`/services/shared/gemini_client.py`) that handles: auth via Workload Identity Federation (no static keys), exponential-backoff retry, structured output validation via Pydantic, token counting + cost logging, safety-setting configuration (BLOCK_NONE for operator-internal; default for guest-facing).
- **Prompt management:** All prompts in `/prompts/` as versioned markdown files. Loaded via `PromptRegistry`. Every agent records `prompt_hash` in audit log.
- **Billing:** Pro is expensive per token. Use Pro only for complex reasoning (cascade prediction, final report). Default to Flash (§15.2). Set per-agent daily token budget with Cloud Monitoring alerts.
- **Failure mode:** If Pro times out or returns invalid output, fall back to Flash with simplified prompt. If both fail, escalate to human.

### §15.2 Gemini 2.5 Flash
- **Purpose:** Fast classification, dispatcher constraint solving, comms drafting, authority reporting. Anything where p95 < 1.5s matters.
- **Integration:** Same SDK. Separate client pool with higher concurrency cap.
- **Special use:** **Multi-modal one-shot classification** — single Flash call receives the CCTV frame bytes + audio snippet transcript + sensor state JSON + venue metadata, and returns a fused classification. This is more token-efficient and lower-latency than separate calls.
- **Structured output:** Use Gemini's JSON mode + Pydantic schema. Reject malformed responses and retry.

### §15.3 Gemini 2.5 Vision (multimodal)
- **Purpose:** Frame analysis in Vision Service.
- **Integration:** Frames from Cloud Storage (signed URL) passed as inline bytes in a `generate_content` call. For video segments (audio context), pass the Cloud Storage URI directly.
- **Cost optimization:** Down-sample frames to 720p before sending. Crop to region of interest after a low-cost motion-detection pass. Use 1 fps baseline; escalate to 5 fps only on suspicion.
- **Prompt engineering:** Strict few-shot template with negative examples. Output schema enforces `{category, sub_type, confidence, evidence_boxes: [BoundingBox], smoke_density: float|null, flame_visible: bool, people_count: int|null}`.

### §15.4 MedGemma
- **Purpose:** Medical triage reasoning in the Triage Agent.
- **Why this is a differentiator:** Most Solution Challenge teams use a generic LLM for "medical" advice. MedGemma is Google's purpose-built open medical model (released 2025). Using it correctly signals to judges that your team understands responsible medical AI.
- **Integration:** Deploy MedGemma to a Vertex AI Endpoint (dedicated, for HIPAA-like isolation). Call via the Vertex AI SDK.
- **Safety envelope:** MedGemma output is NEVER surfaced directly to a guest or non-clinical staff. It is used only to (a) augment the incident brief sent to a credentialed responder, (b) suggest pre-hospital instructions to trained staff from a pre-approved library of instructions (not free-form).
- **Disclaimer handling:** Every MedGemma output carries an explicit "advisory, not medical direction" label in audit.

### §15.5 Vertex AI Agent Engine + Agent Development Kit (ADK)
- **Purpose:** Runtime for the multi-agent system. Handles orchestration loop, tool-use, memory, tracing.
- **Integration:** `pip install google-cloud-aiplatform[agent_engines,adk]`. Agents defined as Python classes inheriting from `vertexai.agents.Agent`. Deployed to Agent Engine for managed runtime + auto-scaling + built-in tracing.
- **Why Agent Engine specifically:** Built-in LangGraph-style graph execution, automatic checkpointing of conversation state, integration with Vertex AI tracing (Cloud Trace compatible), native BigQuery export for session analytics.
- **Local development:** Agents runnable locally via ADK CLI for fast iteration before deploying to Agent Engine.

### §15.6 Vertex AI Matching Engine (vector search)
- **Purpose:** Fast nearest-neighbor search for (a) responder skill matching ("find the responder whose skill vector is closest to the required skill vector"), (b) retrieval-augmented generation for the medical knowledge base used by Triage Agent, (c) similar past incident lookup for the Learning Loop.
- **Integration:** One index per use case. Index `responders-skills-v1` dimension 512. Index `medical-kb-v1` dimension 768 (matching MedGemma embeddings). Index `historical-incidents-v1` dimension 768.
- **Ingestion:** Embeddings generated via Vertex AI Text Embeddings API (`text-embedding-004` or `gemini-embedding-001`).

### §15.7 Vertex AI Search
- **Purpose:** RAG over venue-specific documents (SOPs, floor plans as text, staff manuals, past incident post-mortems).
- **Integration:** Datastore per venue. Documents ingested from Cloud Storage bucket. Queried by agents via SDK.

### §15.8 Vertex AI Pipelines
- **Purpose:** Nightly batch jobs — fine-tuning the classifier on new learning examples, re-embedding the responder skill index, generating cross-venue analytics.
- **Integration:** Kubeflow Pipelines SDK. Pipeline definitions in `/pipelines/`. Triggered via Cloud Scheduler + Cloud Tasks.

### §15.9 Gemini Nano (on-device, future)
- **Purpose:** Guest-phone on-device inference for the sensor fusion feature (P2). Preserves privacy — raw sensor data never leaves phone; only extracted event features.
- **Integration:** Android AI Edge / Flutter plugin. For MVP, stub this with a mock on-device classifier and highlight the architecture in the deck.

### §15.10 Cloud Vision API
- **Purpose:** Structured detection (OCR on guest IDs for lost-and-found, license plate OCR for access logs, Safe Search filter on anything uploaded).
- **Integration:** Client library from Vision Service. Used for low-stakes detection where Gemini is overkill.

## §16. Application & Compute Services

### §16.1 Cloud Run
- **Purpose:** Host every microservice (Ingest, Vision, Audio, Fusion, Dispatch, Comm, Authority, Venue Mgmt, Analytics, Audit, Public API).
- **Why Cloud Run over GKE:** Team of 4; no time for k8s. Cloud Run auto-scales 0→N, per-request billing, built-in HTTPS, zero-ops. Migrate to GKE only when latency SLO requires persistent instances.
- **Config:** `gen2` execution environment, CPU always-allocated for services with background tasks, min instances 1 for services on the hot path (Orchestrator, Dispatch), min 0 elsewhere.
- **Deployment:** `gcloud run deploy` via Cloud Build pipeline (§82). Every service has a Dockerfile in `/services/<svc>/Dockerfile`.
- **Observability:** Automatic Cloud Logging + Cloud Trace. Custom structured logs via `/services/shared/logger.py`.
- **Networking:** VPC connector so services can reach Firestore / BigQuery without public internet hops.

### §16.2 Cloud Functions (Gen 2)
- **Purpose:** Lightweight glue — e.g., Firestore trigger that pushes a new dispatch event to FCM, Cloud Storage trigger on new floor-plan upload to auto-process into an indoor graph.
- **Integration:** TypeScript for Firestore triggers (tight Firebase integration), Python for Cloud Storage / Pub/Sub triggers.

### §16.3 Cloud Build
- **Purpose:** CI/CD. Triggered on GitHub push.
- **Pipeline steps (§82):** Lint → unit test → build image → vulnerability scan → deploy to staging → smoke test → (manual gate) → deploy to prod.
- **Integration:** `cloudbuild.yaml` per service; monorepo root `cloudbuild.master.yaml` orchestrates changed-only builds using `git diff`.

### §16.4 Artifact Registry
- **Purpose:** Store container images, Python packages.
- **Integration:** Cloud Build pushes here. Cloud Run pulls from here. Private registry per environment (staging, prod).

## §17. Data Services

### §17.1 Firestore
- **Purpose:** Live state for everything UIs need to subscribe to — active incidents, responder status, zone status, chat messages.
- **Why Firestore over SQL:** Real-time listeners ("WebSocket feel" for free), offline-first mobile (SDK handles it), scales to millions of concurrent listeners.
- **Collections (§24.1):** `venues`, `incidents`, `incident_events`, `responders`, `staff`, `zones`, `cameras`, `sensors`, `dispatches`, `chat_rooms`, `messages`, `audit_cursor`.
- **Security rules:** Path-based, enforced server-side. Every read/write gated by venue membership + role. Rules co-versioned in `/firebase/firestore.rules`.
- **Indexing:** Composite indexes explicitly defined in `/firebase/firestore.indexes.json`. Never rely on auto-indexing in prod.
- **Scaling:** Per-venue-ID sharding via document ID prefix. Hot documents (active incident) → use document sub-collections, not arrays, to avoid 1MB document limit.
- **Cost discipline:** Listener count is billed. Use `limit` and pagination. Detach listeners on screen dispose in Flutter.

### §17.2 BigQuery
- **Purpose:** (a) Immutable audit log, (b) analytics, (c) learning-loop example store.
- **Dataset layout (§25):** `aegis_audit`, `aegis_analytics`, `aegis_learning`.
- **Partitioning:** Audit table partitioned on `DATE(event_time)`, clustered on `venue_id, incident_id`.
- **Row-level integrity:** Every audit row includes `prev_hash` (SHA-256 of the previous row for same incident) → append-only chain. Tampering detectable via integrity job.
- **Ingestion:** Pub/Sub → BigQuery direct sink (streaming insert). Back-pressure: Pub/Sub buffers up to 7 days if BQ is down.
- **Queryability:** Used by Venue Dashboard via BI Engine cache for sub-second queries.

### §17.3 Cloud Storage
- **Purpose:** Video evidence (frames, short clips), audio blobs, floor plan images, generated reports, evacuation maps.
- **Buckets:**
  - `aegis-evidence-<env>`: raw + redacted frames. Lifecycle: 30 days → Coldline, 180 days → delete unless legal-hold.
  - `aegis-reports-<env>`: generated PDF reports. Retention: 7 years (regulatory).
  - `aegis-venue-assets-<env>`: floor plans, logos.
  - `aegis-models-<env>`: custom fine-tuned model artifacts.
- **Access:** Signed URLs for client reads, service account writes. Uniform bucket-level access ON; no ACLs.
- **Encryption:** CMEK (Customer-Managed Encryption Keys) via Cloud KMS for evidence bucket.

### §17.4 Cloud SQL (Postgres, optional)
- **Purpose:** Relational data that doesn't fit Firestore — billing/subscription data, venue contract metadata, responder credentials with expiry.
- **Integration:** Cloud Run connects via Cloud SQL connector (IAM auth, no password). Schema in `/db/migrations/` using Alembic.
- **Decision:** For MVP, stick to Firestore only. Introduce Cloud SQL in P2 only if needed. YAGNI.

### §17.5 Firebase Realtime Database
- **Purpose:** NOT used. Firestore replaces it for all new use cases. Mentioned here to avoid team confusion.

## §18. Location Services (Google Maps Platform)

### §18.1 Maps SDK for Android / iOS (via Flutter plugin)
- **Purpose:** Render maps in staff and responder apps. Show incident pin, zone overlays, responder routes.
- **Integration:** `google_maps_flutter` package. API key restricted to Aegis Android package + iOS bundle ID + platform-specific SHA-1. Key rotated quarterly.

### §18.2 Maps JavaScript API
- **Purpose:** Maps in venue dashboard and authority console (web).
- **Integration:** `@googlemaps/react-wrapper`. Restricted by HTTP referrer. Loaded with deferred fallback on page load.

### §18.3 Routes API (v2)
- **Purpose:** Compute driving/walking routes for responders.
- **Integration:** Evacuation Agent + Dispatch Service call `routes.googleapis.com`. Use `TRAFFIC_AWARE` for live ETA.
- **Indoor routing:** Routes API doesn't do indoor. For indoor, we use a custom graph solver (§60) with Routes API as fallback for outdoor legs.

### §18.4 Places API
- **Purpose:** Resolve nearby hospitals, fire stations, police stations during venue onboarding.
- **Integration:** Place Text Search + Place Details. Results cached in Firestore `venue.nearby_services` for zero-latency lookup during incidents.

### §18.5 Geocoding API
- **Purpose:** Convert venue address to lat/lng during onboarding; reverse-geocode GPS pings from responders.
- **Integration:** Server-side only; never from clients (key protection).

### §18.6 Maps Static API
- **Purpose:** Generate pre-rendered maps embedded in generated PDF reports.
- **Integration:** Report Service fetches signed static map URLs.

## §19. Communication Services

### §19.1 Firebase Cloud Messaging (FCM)
- **Purpose:** Push notifications to staff / responder / guest phones.
- **Integration:** Dispatch Service → FCM Admin SDK → device tokens stored in Firestore under `/users/{uid}/devices/{deviceId}`.
- **Priority:** `high` for incident dispatch (bypasses Android doze); `normal` for informational.
- **Message structure:** `data` payload only (so the app opens to the right screen with pre-fetched context). Notification rendering done client-side.
- **Topic subscriptions:** Each staff device subscribes to `venue_<id>_staff` and `venue_<id>_zone_<zone>`.

### §19.2 Cloud Translation API (Advanced)
- **Purpose:** Multi-lingual guest instructions. Also staff-interface localization fallback.
- **Integration:** Comms Agent → Translation API. Cached aggressively (same instruction + same language = cache hit).
- **Glossary:** Custom glossary for safety terms (e.g., "assembly point" → "ikhatthā hone kā sthān" in Hindi, not a literal mis-translation) in `/i18n/glossary/`.

### §19.3 Cloud Text-to-Speech
- **Purpose:** Voice PA announcements. Voice prompts in responder brief.
- **Integration:** Comms Agent → TTS → audio file → venue PA API (vendor-specific integration) or responder phone audio stream.
- **Voice selection:** Neural2 voices per language. Calm, non-panic tone selected.

### §19.4 Cloud Speech-to-Text
- **Purpose:** Transcribe audio from (a) CCTV microphones for Audio Service, (b) responder voice notes in the field, (c) guest SOS voice commands.
- **Integration:** Streaming recognition for real-time needs; batch for evidence archival. Language auto-detect for guest audio (common 5 languages).

### §19.5 Firebase In-App Messaging
- **Purpose:** Announcements to staff apps (e.g., "drill scheduled for 3 PM").
- **Integration:** Sparingly; most comms go through FCM.

### §19.6 Email / SMS (SendGrid + MSG91)
- **Purpose:** Next-of-kin SMS (India market — SMS remains the most reliable), authority email with PDF incident packet.
- **Integration:** Not Google-native. SendGrid for email, MSG91 for SMS. Secrets in Secret Manager. These are explicitly called out as non-Google dependencies in the tech dependency matrix.

## §20. Infrastructure Services

### §20.1 Cloud Pub/Sub
- **Purpose:** Event bus (§14).
- **Integration:** One project-level Pub/Sub. Topics + subscriptions created via Terraform (§83). Publishers use the client library; subscribers use push (Cloud Run) or pull (Dataflow) patterns.
- **Ordering keys:** `venue_id:incident_id` for incident-related topics to preserve per-incident order.
- **Schema registry:** Every topic has a schema in `/pubsub-schemas/<topic>.proto`. Publishers validate before send.

### §20.2 Cloud Tasks
- **Purpose:** Delayed/scheduled work — e.g., "if responder doesn't acknowledge in 15 seconds, escalate"; "auto-close incident if unresolved after 4 hours".
- **Integration:** Task queue per purpose (`escalation_queue`, `auto_close_queue`). Tasks dispatched to Cloud Run service endpoints.
- **Why not simple in-memory timers:** Cloud Run instances can be GC'd; in-memory timers don't survive. Tasks are durable.

### §20.3 Cloud Scheduler
- **Purpose:** Cron — nightly analytics refresh, weekly venue compliance digest email, hourly responder-credential expiry check.
- **Integration:** Schedulers defined in Terraform. Each hits a Cloud Run endpoint secured by OIDC token.

### §20.4 Cloud Workflows (optional)
- **Purpose:** Long-running orchestrations that aren't agent-based — e.g., monthly billing aggregation.
- **Decision:** Use Pub/Sub + Cloud Functions instead unless we hit a case that needs Workflows specifically. YAGNI.

### §20.5 Cloud Load Balancing + Cloud Armor
- **Purpose:** Public edge for the web dashboard and authority console. DDoS protection. WAF rules.
- **Integration:** HTTPS LB in front of Cloud Run. Cloud Armor policies in `/terraform/security.tf`.

### §20.6 Cloud CDN
- **Purpose:** Serve static assets (dashboard JS bundles, floor plan images for logged-in venue users).
- **Integration:** Backend bucket for static, backend service for dynamic (with cache keys tuned).

### §20.7 Identity-Aware Proxy (IAP)
- **Purpose:** Gate access to internal tools (admin dashboard, Looker dashboards) to @aegis.ai domain users without any custom auth code.
- **Integration:** Enabled on LB backend. Roles granted via IAM.

### §20.8 Cloud DNS
- **Purpose:** aegis.ai, api.aegis.ai, staff.aegis.ai, responder.aegis.ai, console.aegis.ai, authority.aegis.ai.
- **Integration:** Managed zone in Terraform.

## §21. Security Services

### §21.1 Firebase Auth + Identity Platform
- **Purpose:** Primary auth. Phone-number-based for staff (most hotel staff don't have company emails); email for corporate admins; SSO for authority console.
- **Integration:** Flutter `firebase_auth`. Web `firebase/auth`. Custom claims for RBAC (role, venue_id, skills).
- **MFA:** Required for corporate admins and authority console. Optional for staff.
- **Session:** 1h ID token, 30d refresh token, revocable via admin UI.

### §21.2 Firebase App Check
- **Purpose:** Prevent non-Aegis clients (scripts, replay attacks) from calling Aegis APIs.
- **Integration:** App Check tokens attached to every Firebase + custom-backend call. Backend validates via Admin SDK.
- **Attestation:** Play Integrity on Android, App Attest on iOS, reCAPTCHA Enterprise on web.

### §21.3 reCAPTCHA Enterprise
- **Purpose:** Public form endpoints (contact us, demo request). Bot protection.
- **Integration:** Script in the marketing site + server-side verification.

### §21.4 Secret Manager
- **Purpose:** All secrets — API keys for SendGrid, MSG91, venue-specific PA system creds, signing keys for authority webhooks.
- **Integration:** Services mount secrets via the Cloud Run secrets integration. Rotation policies defined for every secret.
- **Never in code, never in env vars** (except via Cloud Run's secret-env binding which pulls from Secret Manager).

### §21.5 Cloud KMS
- **Purpose:** CMEK keys for Cloud Storage evidence bucket. Signing keys for authority webhook signatures.
- **Integration:** Keys in a dedicated `aegis-crypto` project with locked-down IAM. Auto-rotation every 90 days.

### §21.6 Cloud DLP
- **Purpose:** Redaction of PII in video frames (license plates, faces of non-consenting guests), audio transcripts (names, IDs), and generated reports before sharing outside the venue.
- **Integration:** `dlp.projects.deidentify` API called before any frame is stored beyond the hot buffer. Templates per info-type.

### §21.7 Security Command Center
- **Purpose:** Central security posture dashboard — misconfigurations, vulns, IAM anomalies.
- **Integration:** Standard tier enabled on the project.

### §21.8 VPC Service Controls
- **Purpose:** Perimeter around the evidence project so exfiltration is prevented at the network level.
- **Integration:** Phase 3 / post-MVP. Mentioned in deck for enterprise credibility.

## §22. Observability Services

### §22.1 Cloud Logging
- **Purpose:** All structured logs from all services.
- **Log format:** JSON with `severity`, `trace_id`, `venue_id`, `incident_id`, `agent`, `message`, `context`. Enforced via `/services/shared/logger.py`.
- **Retention:** 30 days default; audit logs 7 years in a separate log bucket.

### §22.2 Cloud Trace
- **Purpose:** Distributed tracing across services. Every incident has an end-to-end trace.
- **Integration:** OpenTelemetry instrumentation. Trace context propagated via Pub/Sub message attributes.
- **Value in demo:** At Grand Finale, show a trace of "signal → dispatch → acknowledge" in 8 seconds live. Judges love this.

### §22.3 Cloud Monitoring
- **Purpose:** Metrics + alerts. Dispatch Latency p95, FPR, agent error rate, Pub/Sub DLQ depth, cost by service.
- **Integration:** Custom metrics emitted via OTEL. Dashboards in `/monitoring/dashboards/`. Alert policies in `/monitoring/alerts/`.

### §22.4 Cloud Profiler
- **Purpose:** Find hot code paths in services (cheaper inference, faster response).
- **Integration:** Auto-attached to Cloud Run services via env var.

### §22.5 Error Reporting
- **Purpose:** Aggregate exceptions across services.
- **Integration:** Automatic from Cloud Logging structured errors.

### §22.6 Firebase Crashlytics
- **Purpose:** Mobile app crashes.
- **Integration:** Flutter plugin. Critical crashes page on-call.

### §22.7 Firebase Performance Monitoring
- **Purpose:** App performance (cold start, screen render time, network trace).
- **Integration:** Flutter plugin.

---

# PART V — DATA MODEL

## §23. Core Entities

### Venue
Physical deployment. Owns zones, cameras, sensors, staff, nearby services.

### Zone
A logical area within a venue (floor, hall, stairwell, exit). Has an indoor graph node ID, max occupancy, accessibility flags, attached cameras/sensors.

### Camera / Sensor
Physical sensors. Metadata: model, location (zone + lat/lng + height), stream URL, sampling config.

### Staff
Hotel employees. Attributes: role, shift, current zone, language preferences, skills, FCM device tokens.

### Responder
Credentialed first responder (internal or external). Attributes: skills (vector), availability status, current location, certifications (with expiry), response radius.

### Guest
End user. Attributes: minimal (phone number if opted in, language, accessibility needs, room). Maximum privacy.

### Incident
The core record. Lifecycle per §9.1. Attributes: id, venue_id, zone_id, category, sub_type, severity, timeline of events, dispatches, triage, evacuation, resolution, post-report.

### Dispatch
One per responder per incident. Attributes: responder_id, role, paged_at, acknowledged_at, en_route_at, arrived_at, handed_off_at, notes.

### Triage
One per medical incident. Attributes: ESI, acuity, symptoms, MedGemma_reasoning (with version), pre_hospital_instructions, vitals.

### EvacuationPlan
One per S1/S2 incident. Attributes: affected_zones, routes[], assembly_point, multilingual_announcements, completed_zones.

### Audit Event
Every state transition, every agent call, every human override.

### Post-Incident Report
Generated within 48h of resolution. Sendai-compliant structure.

## §24. Firestore Data Model

### §24.1 Collection schema
```
/venues/{venueId}
  fields: name, address, geo, timezone, size_sqm, max_occupancy,
          settings { autonomous_mode_enabled, dispatch_latency_sla_seconds,
                     languages_supported[], drill_mode_enabled },
          nearby_services { ambulance_stations[], fire_stations[], hospitals[], police[] }
  subcollections:
    zones/{zoneId}: name, type, floor, graph_node_id, capacity, camera_ids[], sensor_ids[], exit_count, accessible
    cameras/{cameraId}: zone_id, rtsp_url, model, lat, lng, z_m, active, last_frame_at
    sensors/{sensorId}: zone_id, type (smoke|co|heat|motion|door), last_reading, last_reading_at
    staff/{staffId}: user_id, role, shift_id, languages[], skills[], zone_assignment, active
    responders/{responderId}: user_id, internal|external, credentials[], skill_vector_id, availability_status
    chat_rooms/{roomId}: type (incident|venue|shift), members[], pinned
    chat_rooms/{roomId}/messages/{messageId}: sender_id, text, attachments[], sent_at, read_by[]

/incidents/{incidentId}
  fields: venue_id, zone_id, category, sub_type, severity, status,
          detected_at, resolved_at, confidence, agent_trace_id,
          summary (human-readable, 140 chars, generated by Comms Agent)
  subcollections:
    signals/{signalId}: perceptual_signal payload
    events/{eventId}: state transitions (DETECTED → CLASSIFIED → ...)
    dispatches/{dispatchId}: full Dispatch schema
    triage/{triageId}: Triage schema (only if medical)
    evacuation/{planId}: EvacuationPlan schema
    comms/{commId}: every generated communication
    overrides/{overrideId}: human-in-the-loop interventions

/users/{uid}
  fields: phone, email, display_name, preferred_language,
          accessibility { screen_reader, high_contrast, large_text }
  subcollections:
    devices/{deviceId}: fcm_token, platform, model, last_seen_at
    memberships/{venueId}: role, skills[], joined_at

/audit_cursor/{serviceName}
  field: last_event_id_processed
```

### §24.2 Security rules (excerpt)
```js
match /incidents/{incidentId} {
  allow read: if request.auth != null
    && (resource.data.venue_id in get(/databases/$(database)/documents/users/$(request.auth.uid)).data.venue_memberships
        || request.auth.token.role == 'authority_reviewer');
  allow write: if false; // writes only via backend with admin SDK
}
match /incidents/{incidentId}/dispatches/{dispatchId} {
  allow read: if isVenueMember(resource.data.venue_id);
  allow update: if isDispatchTarget(dispatchId) &&
    onlyChangedAllowedFields(['acknowledged_at', 'en_route_at', 'arrived_at', 'notes']);
}
```

## §25. BigQuery Schema

### §25.1 Audit dataset `aegis_audit`
```sql
CREATE TABLE aegis_audit.events (
  event_id STRING NOT NULL,
  event_time TIMESTAMP NOT NULL,
  venue_id STRING NOT NULL,
  incident_id STRING,
  actor_type STRING,   -- 'agent' | 'human' | 'system'
  actor_id STRING,
  action STRING,
  input_hash STRING,
  output_hash STRING,
  prev_hash STRING,    -- chain integrity
  row_hash STRING,     -- SHA-256(event_id || event_time || venue_id || ... || prev_hash)
  model_version STRING,
  confidence FLOAT64,
  explanation STRING,
  extra JSON
)
PARTITION BY DATE(event_time)
CLUSTER BY venue_id, incident_id;
```

Append-only. Daily integrity job verifies `row_hash` chain; alerts on break.

### §25.2 Analytics dataset `aegis_analytics`
Views built on top of audit:
- `v_dispatch_latency_by_venue_daily`
- `v_false_positive_rate_by_camera_weekly`
- `v_incident_volume_by_category_hourly`
- `v_responder_sla_by_responder_weekly`

### §25.3 Learning dataset `aegis_learning`
Structured resolved-incident records used for fine-tuning:
```sql
CREATE TABLE aegis_learning.classifier_training_examples (
  example_id STRING,
  venue_id STRING,
  incident_id STRING,
  frames_uri STRING,
  audio_uri STRING,
  sensor_state JSON,
  classified_as STRING,
  ground_truth STRING,   -- set after retrospective review
  agreement BOOL,
  created_at TIMESTAMP
);
```

## §26. Vertex AI Matching Engine Indexes

### §26.1 `responders-skills-v1`
- Dimension: 512
- Use case: matching required_skills → available responders
- Embedding model: custom (skills encoded via a small supervised model trained on skill_name + description)
- Refresh: nightly

### §26.2 `medical-kb-v1`
- Dimension: 768
- Use case: RAG for Triage Agent
- Content: curated first-aid procedures, ESI examples, Indian ambulance service protocols
- Embedding: `text-embedding-004`

### §26.3 `historical-incidents-v1`
- Dimension: 768
- Use case: "have we seen this pattern before at this venue?" — given a new classification, retrieve top-5 similar past incidents
- Content: text summary of each resolved incident
- Update: on every incident close

---

# PART VI — BACKEND SERVICES

Each service is a Cloud Run container. Monorepo path `/services/<name>`. Common shared libraries in `/services/shared` (Python) or `/packages/shared` (TypeScript for TS-based Cloud Functions).

## §27. Ingest Service
- **Path:** `/services/ingest`
- **Stack:** Python 3.12, FastAPI, `google-cloud-storage`, `google-cloud-pubsub`
- **Responsibility:** Accept HTTPS POST of frames (from edge gateway or demo BYO-webcam), audio chunks, sensor events. Validate App Check. Write to Cloud Storage + publish to raw topic.
- **Endpoints:**
  - `POST /v1/frames` multipart with camera_id, timestamp, jpeg bytes
  - `POST /v1/audio` multipart with mic_id, timestamp, pcm bytes
  - `POST /v1/sensor_events` JSON array
  - `POST /v1/webrtc-offer` SDP offer for browser-demo video push
- **Auth:** Firebase App Check token + (for edge gateway) mTLS via signed device certs from Cloud KMS

## §28. Vision Service
- **Path:** `/services/vision`
- **Stack:** Python 3.12, FastAPI, `vertexai`, `google-cloud-pubsub`
- **Responsibility:** Consume `raw_frames` topic. Apply motion pre-filter (skip frames with no change to save cost). Call Gemini Vision. Apply Cloud DLP redaction to output evidence. Emit `perceptual_signals`.
- **Key class:** `FrameAnalyzer` with methods: `pre_filter(frame) -> bool`, `analyze(frame, context) -> VisionSignal`, `redact_and_store(frame) -> storage_uri`.
- **Caching:** Venue × camera × recent-frame-hash cache (redacted Redis via Memorystore) to skip duplicate analyses.

## §29. Audio Service
- **Path:** `/services/audio`
- **Stack:** Python, FastAPI, Gemini Audio SDK
- **Responsibility:** Detect audio events — scream, glass break, fire alarm, smoke alarm, gunshot, crash, distress shouting. Emit `perceptual_signals`.

## §30. Sensor Fusion Service
- **Path:** `/services/fusion`
- **Responsibility:** Correlate signals within a spatio-temporal window (same zone, ±10s). Assign unified `fused_signal_id`. Emit `fused_signals`.
- **Algorithm:** Per-zone sliding window, greedy coalescence, priority weighting by signal modality.

## §31. Orchestrator Service
- **Path:** `/services/orchestrator`
- **Responsibility:** Host the Orchestrator Agent. Consume `fused_signals`. Drive the agent loop. Write to Firestore + BigQuery audit + `incident_events`.
- **Runtime:** Long-running on Vertex AI Agent Engine; Cloud Run service is a thin wrapper that streams signals to Agent Engine sessions.

## §32. Dispatch Service
- **Path:** `/services/dispatch`
- **Responsibility:** Accept `dispatch_events`. Resolve to specific responders. Send FCM. Manage acknowledge / timeout / escalation. Maintain active-dispatch state in Firestore.
- **Critical code:** The escalation ladder state machine — this is life-safety, needs 100% test coverage and property-based tests.

## §33. Triage Service
- **Path:** `/services/triage`
- **Responsibility:** Wraps the MedGemma endpoint with strict input/output validation. Serves Triage Agent tool calls.
- **Safety:** Hard-coded allow-list of output categories. Any out-of-schema output is rejected and logged. Fallback to a pre-approved instruction template if model unavailable.

## §34. Evacuation Service
- **Path:** `/services/evacuation`
- **Responsibility:** Compute evacuation plans. Integrates venue indoor graph (§60), Maps Routes API for external legs, and crowd density snapshot.
- **Output:** Per-zone directive ("clear via staircase B, proceed to assembly point 2") + per-guest card (if phone opted in).

## §35. Communications Service
- **Path:** `/services/comms`
- **Responsibility:** Generate multi-lingual PA scripts, guest push cards, authority incident packets. Invokes Translation + TTS. Sends to correct channels (PA API, FCM, webhook).
- **Template engine:** Jinja2 with validated placeholders. Every template has a glossary-aware i18n table.

## §36. Authority Service
- **Path:** `/services/authority`
- **Responsibility:** Dispatch structured incident packet to configured authority webhook (fire, ambulance, police). Signs payload. Retries with exponential backoff. Fallback to email/SMS.
- **Packet schema:** JSON-LD with schema.org/EmergencyEvent extensions + custom aegis extensions. Signed with venue's private key (Cloud KMS).

## §37. Venue Management Service
- **Path:** `/services/venue`
- **Responsibility:** Onboarding, floor plan upload, zone definition, staff roster, drill management.

## §38. Analytics Service
- **Path:** `/services/analytics`
- **Responsibility:** Serve BigQuery-backed dashboards. Aggregates cached for 60s. Power Venue Dashboard charts.

## §39. Audit Service
- **Path:** `/services/audit`
- **Responsibility:** Append-only writer to BigQuery audit. Computes row hash. Publishes to `audit_events`. Serves read-with-chain-verify for integrity UI.

## §40. Public / Marketing API
- **Path:** `/services/public-api`
- **Responsibility:** Contact forms, demo requests, status page. Rate-limited, reCAPTCHA-protected.

---

# PART VII — FRONTEND APPLICATIONS

## §41. Staff Mobile App (Flutter)
- **Path:** `/apps/staff`
- **Stack:** Flutter 3.x, Dart, `firebase_core`, `firebase_auth`, `cloud_firestore`, `firebase_messaging`, `google_maps_flutter`, Riverpod for state, `flutter_localizations`, `go_router` for navigation.
- **Platforms:** Android (primary — ₹8,000 phone class), iOS (secondary).
- **Offline:** Firestore offline persistence enabled. Outbound mutations queued with retry and conflict resolution.
- **Target cold-start:** < 1.8s on a ₹10k Android.
- **Architecture:** Feature-first (`/lib/features/auth`, `/lib/features/incidents`, `/lib/features/chat`, `/lib/features/drill`). Each feature has `data/`, `domain/`, `presentation/`.
- **Accessibility:** TalkBack tested. Semantic labels on every tappable. Min 48dp tap target. Supports 200% text scale.
- **Languages:** en, hi, gu, ta, bn at launch. ARB files in `/apps/staff/lib/l10n/`.
- **Notifications:** High-priority FCM wakes the app and navigates directly to the incident screen (handled via background handler + deep link).

## §42. Responder Mobile App (Flutter)
- **Path:** `/apps/responder`
- Similar stack. Different home screen: pending dispatches, active incident, credentials, offline maps for responder's response zone.
- Critical feature: offline-cached indoor map for the venues the responder is credentialed at, downloaded on credential grant.

## §43. Guest PWA
- **Path:** `/apps/guest-pwa`
- **Stack:** Next.js 14 (app router), React, TypeScript, Tailwind, `firebase/messaging` for web push.
- **Activation:** Guest scans QR in their room or at venue entry → consent screen → phone verification → opt-in to safety notifications.
- **UX:** Minimal — card showing current venue status (nominal / alert / evacuating), language selector, "I need help" SOS button, accessibility shortcuts.
- **PWA:** Installable, offline-capable (cached evac card for their zone).

## §44. Venue Dashboard (Web)
- **Path:** `/apps/dashboard`
- **Stack:** Next.js 14, React, TypeScript, Tailwind, TanStack Query, `firebase/firestore` for live state, `recharts` for charts, Google Maps JS.
- **For:** Venue GM, ops head, compliance officer.
- **Sections:**
  - Live: active incidents, staff positions, camera grid, zone status
  - History: incident log, search, filter, export
  - Setup: venue config, zones, sensors, staff, drills
  - Compliance: audit trail, generated reports, integrity verifier
  - Analytics: DL trends, FPR, SAR, fairness view
  - Billing: plan, usage, contract

## §45. Authority Console (Web)
- **Path:** `/apps/authority`
- **Stack:** Next.js 14. Authenticated via SSO (SAML for police/fire departments that have one; email/OTP otherwise).
- **For:** Civic authorities (fire, police, 108).
- **Sections:**
  - Live feed of incidents from venues that have opted to share with this authority
  - Incident detail (structured packet, video evidence with DLP redaction, responder assignments)
  - Historical search
  - Export for investigations (signed evidence bundle)

---

# PART VIII — DESIGN SYSTEM

## §46. Design Principles
1. **Information over ornament.** Staff is looking at this app while trying to save a life. Every pixel serves the decision.
2. **Urgency without panic.** Visual design conveys seriousness, not chaos. No flashing red. One calm color per severity.
3. **Glanceable.** Every active-incident screen must convey "what's happening, where, who's on it" in < 1.5 seconds.
4. **Accessibility is not a feature.** Every UI state works with a screen reader and at 200% text scale.
5. **Bilingual-first.** No UI is designed English-first and then translated. Layouts accommodate Devanagari, Tamil, Bengali glyph heights.
6. **Calm defaults.** Dark canvas for operators (low-light friendly). Reserve color for signaling.

## §47. Color System

```
/* Canvas */
--c-bg-primary:      #0A0E14   /* graphite, dark */
--c-bg-elevated:     #121821   /* cards */
--c-bg-surface:      #1A2230   /* modals, sheets */
--c-bg-inverse:      #F8FAFC   /* light theme bg */

/* Ink */
--c-ink-primary:     #F1F5F9
--c-ink-secondary:   #94A3B8
--c-ink-muted:       #64748B
--c-ink-inverse:     #0F172A

/* Semantic */
--c-status-ok:       #10B981   /* nominal, resolved */
--c-status-watch:    #3B82F6   /* monitoring */
--c-status-warn:     #F59E0B   /* S3 alert */
--c-status-urgent:   #EF4444   /* S2 urgent */
--c-status-critical: #DC2626   /* S1 critical */
--c-status-action:   #14B8A6   /* brand accent; action buttons */

/* Borders */
--c-border:          #1E293B
--c-border-strong:   #334155
--c-border-focus:    #14B8A6
```

Contrast ratios all pass WCAG AA against their intended backgrounds.

## §48. Typography Scale

```
--font-display:   'Inter Display', system-ui, sans-serif
--font-ui:        'Inter', system-ui, sans-serif
--font-mono:      'JetBrains Mono', ui-monospace, monospace

--size-xs:   12px / 16px
--size-sm:   14px / 20px
--size-base: 16px / 24px
--size-md:   18px / 28px
--size-lg:   24px / 32px
--size-xl:   32px / 40px
--size-2xl:  48px / 56px    /* incident title on detail screen */
```

In Devanagari, line-heights are 1.1× Latin line-heights to accommodate matras.

## §49. Spacing, Grid, Radius

```
4 / 8 / 12 / 16 / 20 / 24 / 32 / 48 / 64 / 96   /* spacing scale */
12-col grid at ≥1024px; 4-col at <1024px; 1-col <640px
Radius: 4 (inputs), 8 (cards), 12 (modals), 999 (pills)
Elevation: 0 (flat), 1 (card on bg), 2 (hover), 3 (modal)
```

## §50. Component Library (Flutter + React in parallel)

Every component in both Flutter (`/packages/ui_flutter`) and React (`/packages/ui_web`) with identical props where feasible.

- **Button** (primary, secondary, ghost, destructive)
- **StatusPill** (ok/watch/warn/urgent/critical)
- **IncidentCard** (compact / full)
- **SeverityBadge** (S1/S2/S3/S4)
- **TimelineEvent** (event in an incident timeline)
- **ZonePin** (on map)
- **ResponderAvatar** (status dot indicating availability)
- **DispatchCard** (actionable: Accept/Escalate/Decline)
- **AgentTraceView** (for explainable-AI — shows agent reasoning steps)
- **LiveVideoTile** (with privacy toggle and freeze-frame for evidence)
- **EvacuationRouteStrip** (mini-map of one route)
- **LanguagePicker** (flag + native name)
- **SOSButton** (giant, accessible, confirmation)
- **CountdownRing** (for 15s acknowledge timeout)
- **EmptyState**, **LoadingState**, **ErrorState** (standard three)
- **AuditRow** (in audit log table)
- **IntegrityBadge** (shows audit chain is intact)

## §51. Motion Design
- **Enter**: 240ms, ease-out. **Exit**: 160ms, ease-in.
- **Emergency banner slide-in**: 320ms spring.
- **Urgent pulse**: scale 1 → 1.04 → 1 over 1.4s, only on S1.
- **No bouncy animations in operator UIs.** Confidence-reducing.
- **Reduce-motion respected** via `MediaQuery.disableAnimations` in Flutter and `prefers-reduced-motion` on web.

## §52. Emergency Mode
When an S1 incident is active, staff app switches to Emergency Mode:
- Background becomes `#1A0A0A` (very dark red-tinted)
- Header pinned with incident ID, timer, one-tap escalation
- Non-essential navigation hidden
- All buttons enlarged 20%
- Audio cue (subtle, once) on state change
- Haptic feedback on state change
- Auto-dismisses when incident transitions to RESOLVING

## §53. Accessibility
- WCAG 2.1 AA compliance checked via `axe-core` in CI (web) and `flutter_test` semantic assertions (mobile)
- Focus order explicit on every screen
- Alt text on every image
- Form fields with visible labels (no placeholder-as-label)
- Error messages inline + announced via ARIA live region
- Keyboard shortcuts documented; a "?" overlay
- Voice commands via Speech-to-Text for staff in kitchen environments where touch is impractical (apron, gloves)

---

# PART IX — EVERY SCREEN (SPEC)

I will not enumerate 60 screens one by one, but I will give the canonical screen list per app, and for the 5 most critical screens, a full spec. The rest follow from the design system.

## §54. Staff App Screens
1. Splash + auth (phone OTP)
2. Venue selection (if multi-venue staff)
3. Home (shift, zone, pending dispatches, quick SOS)
4. Active incident list
5. **Incident detail — active** (the most critical screen; spec below)
6. Incident history
7. Chat (rooms + thread)
8. My profile + credentials
9. Drill mode
10. Settings (language, notifications, accessibility)

### §54.1 Screen spec — Incident Detail (Active)

**Purpose:** Allow staff to act on an active incident in under 3 seconds.

**Layout (portrait phone):**
```
┌─────────────────────────────────────────┐
│ ◂ INC-7741 · S2 URGENT            00:47 │  ← Pinned header; back + ID + severity + elapsed
├─────────────────────────────────────────┤
│                                          │
│   KITCHEN FIRE                           │  ← 32pt; incident title (Comms Agent one-liner)
│   Main kitchen · Floor 1                 │  ← 16pt; location
│                                          │
│   [ map / CCTV thumbnail with indicator ]│  ← Swipeable: live feed (privacy) / indoor map
│                                          │
├─────────────────────────────────────────┤
│  YOUR ACTION                             │
│                                          │
│  ┌───────────────────────────────────┐   │
│  │  1. Proceed to Main Kitchen now   │   │
│  │  2. Confirm extinguisher deployed │   │
│  │  3. Clear 10m perimeter           │   │
│  └───────────────────────────────────┘   │
│                                          │
│  [  I'M ON IT  (countdown 12s)  ]        │  ← Primary action with acknowledge timer
│  [  Escalate  ]   [  Need help  ]        │
├─────────────────────────────────────────┤
│  DISPATCHED                              │
│  • You (Priya, Duty Manager) — paged     │
│  • John (Fire Warden) — en route · 40s   │
│  • Fire Service — notified · 12:42       │
├─────────────────────────────────────────┤
│  CASCADE FORECAST                        │
│  If not contained in 90s:                │
│  → gas line risk                         │
│  → 4 guest rooms above affected          │
│  → 1 accessibility flag (Room 312)       │
├─────────────────────────────────────────┤
│  [ View full trace ▾ ]                   │  ← Expands agent reasoning
└─────────────────────────────────────────┘
```

**Components:** IncidentHeader, PrimaryActionButton with CountdownRing, DispatchList, CascadeCard, AgentTraceView (collapsed).

**States:** pre-ack (countdown), ack'd (primary action replaced with "Mark task complete"), en_route, arrived, resolving, resolved.

**Data sources:** Firestore `/incidents/{id}` doc and `/incidents/{id}/dispatches` subcollection (real-time listeners), `/incidents/{id}/events` for timeline.

**Motion:** Severity color animates from bg to border as user ack's. Countdown ring pulses.

## §55. Responder App Screens
1. Splash + auth
2. Home (availability toggle, active page, credentials)
3. Incoming dispatch (full-screen takeover)
4. **En route view** (map + patient brief)
5. Arrived / handoff
6. Report/close
7. History + CME credit log
8. Credentials + expiry warnings

## §56. Guest PWA Screens
1. QR → consent
2. Phone verification
3. Home status (nominal/alert)
4. SOS flow
5. Evacuation card (active only during incident)

## §57. Venue Dashboard Screens
1. Login (SSO)
2. Live overview (all-venue or per-venue)
3. Incident list + filters
4. **Incident detail** (desktop — same data as staff incident detail, richer view)
5. Venue setup (5 sub-screens)
6. Staff & responders
7. Drills
8. Analytics (6 sub-dashboards)
9. Compliance + reports
10. Integrity view (audit chain)
11. Billing
12. Settings + API keys

## §58. Authority Console Screens
1. SSO login
2. Live feed of incidents from opted-in venues
3. Incident detail (with video evidence, redacted appropriately)
4. Historical search
5. Export / evidence bundle
6. Responder coordination
7. Audit + compliance

---

# PART X — NOVEL TECHNICAL CONTRIBUTIONS (INNOVATION MOAT)

These are the *specific* pieces judges can point to and say "nobody else built this." They collectively unlock ~5 extra points on Innovation and ~5 extra points on Technical Merit.

## §59. Cascade-Aware Incident Classifier

**Problem:** Standard classifiers label the current state. Emergencies are trajectories — a small kitchen fire that will reach a gas line in 90s is a different incident than a small kitchen fire that won't.

**Approach:** Two-stage model.
1. **Base classifier** (Gemini 2.5 Flash) labels the current perceptual signal.
2. **Cascade predictor** (Gemini 2.5 Pro with venue-graph context) takes base label + spatial context + historical base rates → produces a 30s/90s/300s forecast probability vector over a taxonomy of cascade outcomes (vertical smoke spread, crowd surge, gas-line proximity, structural failure proximity).

**Data input to cascade predictor:**
- Current signal JSON
- Venue graph subgraph centred on the affected zone (nodes: adjacent zones, edges: corridors/stairs with attributes like airflow, ventilation, max occupancy)
- Current zone occupancy estimates (from camera crowd density)
- Time-of-day base rates for this venue
- Known high-risk attributes (gas line, disability flag, etc.)

**Output schema:**
```json
{
  "predictions": [
    {"horizon_s": 30, "outcome": "contained", "prob": 0.62},
    {"horizon_s": 30, "outcome": "vertical_smoke_spread", "prob": 0.18},
    {"horizon_s": 90, "outcome": "gas_line_proximity_breach", "prob": 0.21},
    {"horizon_s": 90, "outcome": "adjacent_zone_smoke", "prob": 0.33},
    {"horizon_s": 300, "outcome": "multi_floor_spread", "prob": 0.09}
  ],
  "recommended_preemptive_actions": [
    {"action": "pre-alert_rooms_312_412", "trigger_horizon_s": 60},
    {"action": "stage_fire_service", "trigger_horizon_s": 90}
  ],
  "rationale": "..."
}
```

**Why judges will love this:**
- It's a genuinely novel product/modeling framing — not "LLM labels an image" but "LLM forecasts cascade trajectory under venue constraints"
- It's explainable (rationale field)
- It directly enables pre-emptive action, which maps to the "prevention not just response" narrative

**Evaluation plan:**
- Simulated replay of 20 synthetic cascade scenarios; compare against baseline no-cascade classifier
- Report Brier score and pre-emptive action precision in the deck

## §60. Triage-Constrained Dispatcher

**Problem:** Naive "send the nearest responder" fails when the nearest responder lacks the needed skill, can't speak the patient's language, or is off-shift.

**Approach:** Formulate dispatch as a constraint satisfaction problem (CSP), solved with a small Gemini-guided optimizer:

```
Variables:  x_r ∈ {0,1} for each available responder r
Constraints:
  Σ x_r = 1 for primary (unless S1 requires multi-dispatch)
  x_r = 0 if skill_vector_r · required_skills < skill_threshold
  x_r = 0 if cred_expiry_r < now
  x_r = 0 if shift_status_r != 'on'
  x_r = 0 if distance_r > max_eta_seconds × walking_speed
  language_match: soft preference via objective
Objective:
  minimize ETA_r + λ₁·(1 - skill_score_r) + λ₂·(1 - lang_score_r)
         + λ₃·workload_r
```

**Solver:** For up to ~30 responders per venue, a pure Python integer-LP solver (PuLP + CBC) is fast enough. For larger responder pools, use a greedy heuristic then Gemini re-ranks the top 3 using contextual reasoning about the specific patient.

**The "Gemini re-rank" trick:** The optimizer narrows to top-3 candidates by objective. Gemini sees the *full* structured context — patient acuity, responder recent history, known language preferences — and picks the best. This blends symbolic optimization (fast, proven) with LLM contextual reasoning (nuanced, soft-constrained). **This hybrid is the specific novelty to name.**

## §61. Privacy-Preserving Guest-Phone Sensor Fusion

**Problem:** CCTV coverage is sparse in hotel rooms, wedding venues' outdoor areas, religious gathering peripheries. Guest phones have accelerometers, mics, cameras that could dramatically expand perception, but raw sensor upload is a privacy nightmare and a bandwidth nightmare.

**Approach:** On-device feature extraction with opt-in consent.
1. Guest installs Aegis Safety PWA or native Flutter app (opt-in via QR during onboarding).
2. On-device wake-word model (small Gemini Nano or tflite model) listens for "help" in 5 languages.
3. On-device accelerometer classifier detects falls.
4. On-device mic snippet classifier detects screams/glass break (1s windows).
5. **Only the classifier output (label, confidence, timestamp, coarse location) leaves the device.** Raw audio/video never uploads.
6. Uploaded events go into Sensor Fusion Service, which correlates with CCTV + IoT signals.

**Privacy statement (consent screen language):** *"Your phone will listen for sounds like 'help' and detect falls while you're at the venue. Audio and video are analyzed entirely on your phone. Only the result — 'fall detected' or 'help called' — is sent to venue safety, never your voice or photos. You can turn this off in Settings."*

**For MVP:** We can ship the server side + a mock mobile client that simulates on-device classification. The *architecture* is the novelty; the exhaustive on-device models are Phase-3 stretch.

## §62. Post-Incident Learning Loop

**Problem:** Every incident is a potential dataset. Most systems waste it.

**Approach:** On every incident close, a Vertex AI Pipeline runs:
1. Pulls all signals, classifier outputs, agent traces, final resolution status from BigQuery.
2. Constructs a training example: `(raw_multimodal_input, ground_truth_category, human_corrections, severity_trajectory)`.
3. Stores in `aegis_learning.classifier_training_examples` with per-venue and global tags.
4. Weekly, a fine-tuning job runs on a Gemma base model using LoRA on the accumulated examples. Evaluated against a hold-out set.
5. New model deployed to a canary Vertex AI Endpoint. A/B tested on live traffic (1% of venues).
6. Promoted or rolled back.

**Visible to judges:** An "Accuracy over time" chart in the Venue Dashboard. Line going up and to the right. Extremely compelling for the Grand Finale deck.

## §63. Crowd-Density Aware Evacuation Routing

**Problem:** Evacuation routing with Maps Routes API alone gives each guest the shortest path, which guarantees a bottleneck at the exit nearest the incident.

**Approach:**
1. **Indoor graph:** Every venue has a graph `G = (V, E)` where V is zones/nodes and E is corridors with attributes `(length, width, max_flow_persons_per_minute, accessibility, stairs_count)`.
2. **Live density estimates** per zone from camera feeds.
3. **Flow-aware routing:** Not shortest path; *flow-balanced* paths. Minimize `max over edges (flow_e / capacity_e)` — the Braess-paradox-aware routing that traffic engineers use for real evacuations.
4. **Per-guest personalization:** Each guest's card shows *their* recommended route based on current density. As density shifts, routes update via FCM push. (Not every 3 seconds — a staleness threshold prevents flicker.)
5. **Staff override:** Staff with visual on a corridor can flag it blocked via one tap, immediately re-routes propagate.

**Algorithm:** Min-cost max-flow variant with time-expanded graph (standard in evacuation literature). Implementation in `networkx` + a custom flow solver. For MVP, ship shortest-path and mock the flow-aware upgrade in the deck.

---

# PART XI — SECURITY & PRIVACY

## §64. Authentication Architecture

Three auth surfaces, all through Firebase Auth + Identity Platform:
1. **Staff / Responder (mobile):** Phone OTP. After login, custom claims `{role: 'staff'|'responder', venues: [...], skills: [...]}` set via Admin SDK in a Cloud Function triggered by role change.
2. **Corporate (web dashboard):** Email + password with MFA. Corporate SSO via SAML for enterprise tier.
3. **Authority (web console):** SSO only (SAML), with OTP fallback.

Tokens validated on every backend call via Firebase Admin SDK (`verifyIdToken`). App Check token required alongside ID token — missing App Check token → 403.

## §65. RBAC Matrix (excerpt)

| Role | Incidents | Staff roster | Venue config | Audit | Export evidence |
|---|---|---|---|---|---|
| Staff | Read (own venue) + ack | Read self | — | — | — |
| Senior staff | Read/write (own venue) | Read team | — | — | — |
| Duty manager | Read/write (own venue) | Read/write team | Read | Read | — |
| Venue GM | Read/write | Read/write | Read/write | Read | Read |
| Corp admin | Read (venues owned) | — | Read/write | Read | Read |
| Auditor | Read all | — | Read | Read + verify chain | Read |
| Authority reviewer | Read (opted-in venues) | — | — | Read | Signed export |
| Responder | Own dispatches | — | — | — | — |
| Super-admin (Aegis) | — | — | — | Chain verification only | — |

Every role granted via custom claims. Rules enforced at three layers: Firestore rules, backend middleware, UI affordance (hide what you can't do).

## §66. Encryption
- **In transit:** TLS 1.3 everywhere. mTLS between edge gateway and Ingest API.
- **At rest:** Default encryption everywhere; CMEK for the evidence bucket.
- **In use:** Confidential Space (optional, P3) for the evidence redaction pipeline.

## §67. PII Handling
- **Guest PII:** Phone number, language, room. Nothing else unless explicitly provided by guest. Stored in a separate `guest_profiles` collection with stricter rules.
- **Video frames:** Every frame passing into long-term storage is first run through Cloud DLP with a face-detection redactor + license-plate + ID-card redactor. Raw (un-redacted) frames exist only in a hot buffer with 60-minute retention and access gated to auditor role during an active legal hold.
- **Audio transcripts:** Run through DLP before any non-incident-handling read.
- **Right-to-be-forgotten:** Per-guest deletion request triggers a cascade that purges their guest profile and nullifies their ID in all audit rows (audit rows themselves are immutable, but PII fields are redacted).

## §68. On-Device Processing for Guest-Phone Mode (§62)
Hard rule: raw audio/video sensor data never leaves a guest's phone.

## §69. Audit Logging
Every action is logged with the hash chain scheme in §25.1. A daily Cloud Scheduler job runs a verifier that reports chain integrity to Cloud Monitoring. Any break alerts the team immediately.

## §70. Compliance Frameworks Targeted
- **Sendai Framework for Disaster Risk Reduction (2015–2030):** Our post-incident report schema aligns with the Sendai monitor indicators.
- **India DPDP Act 2023:** Consent, purpose limitation, deletion rights implemented.
- **India HRACC hotel classification norms:** Safety requirements that Aegis helps auto-document.
- **India NDMA guidelines for mass gatherings:** Aegis helps meet the 2014 NDMA guidelines.
- **SOC 2 Type II (post-hackathon):** Mentioned in the deck as roadmap.

---

# PART XII — SCALABILITY

## §71. Load Targets
| Tier | Venues | Incidents/day/venue | Cameras/venue | Peak concurrent incidents system-wide |
|---|---|---|---|---|
| MVP demo | 1 | 5 | 10 | 1 |
| Phase 2 pilot | 5 | 3 | 20 | 5 |
| Phase 3 showcase | 20 | 3 | 30 | 20 |
| Year-1 target | 200 | 2 | 40 | 30 |
| Year-2 target | 2,000 | 2 | 50 | 100 |

System engineered with headroom for Year-2 targets.

## §72. Horizontal Scaling
Every service is stateless. Session state in Firestore/Redis. Cloud Run auto-scales on concurrent requests; min instances for hot-path (Orchestrator, Dispatch, Vision). Pub/Sub scales automatically.

## §73. Caching
- **Memorystore Redis:** Vision dedup cache, Translation cache, hot dispatch state.
- **BI Engine:** BigQuery caching for dashboards.
- **CDN:** Static assets.
- **App-level:** Venue config, staff roster cached in Firestore offline persistence.

## §74. Rate Limiting
- **Per-venue quota:** per-second limit on Gemini calls; spill over buffers in Pub/Sub.
- **Per-user:** login attempts, SOS triggers.
- **Abuse protection:** Cloud Armor WAF rules.

## §75. Circuit Breakers
Between services, between Aegis and third-party APIs (PA system, SMS provider). On open circuit, graceful degradation — e.g., if Translation down, fall back to English.

## §76. Regional Strategy
- **MVP:** asia-south1 (Mumbai) — proximity for Indian users, good Gemini availability.
- **Backup region:** asia-south2 (Delhi).
- **Data residency:** all Indian-venue data stays in Indian regions (DPDP + potential data localization rules).

---

# PART XIII — API & ROUTING

## §77. REST API Surface (public, for partners + authority console)

Base: `https://api.aegis.ai/v1`

```
POST   /venues                         create venue (admin)
GET    /venues/{id}                    read venue
PATCH  /venues/{id}                    update venue
POST   /venues/{id}/zones              create zone
POST   /venues/{id}/cameras            register camera
POST   /venues/{id}/sensors            register sensor
POST   /venues/{id}/staff              add staff
POST   /venues/{id}/responders         add responder
POST   /venues/{id}/drills             start drill
GET    /venues/{id}/stats              dashboard stats

GET    /incidents/{id}                 incident detail
GET    /incidents/{id}/events          event stream (SSE)
GET    /incidents/{id}/audit           audit export (signed)

POST   /dispatches/{id}/ack            acknowledge
POST   /dispatches/{id}/enroute
POST   /dispatches/{id}/arrived
POST   /dispatches/{id}/handoff

POST   /reports/{id}/generate          generate PDF report
GET    /reports/{id}                   download PDF
POST   /evidence/{id}/export           export evidence bundle

POST   /authority/webhooks             register authority webhook
POST   /authority/webhooks/test        send test event
```

All endpoints: OpenAPI spec in `/docs/openapi.yaml`. Auto-generated SDKs (TS, Python, Go, Dart) published to Artifact Registry.

## §78. Real-time Channels
- **Firestore listeners** handle most UI-reactive needs.
- **Server-Sent Events** on `/incidents/{id}/events` for authority console (no Firebase dependency required).
- **WebRTC data channel** in demo for staff radio-style PTT.

## §79. Internal Pub/Sub Topics (§14) with schemas in `/pubsub-schemas/`.

## §80. Webhook Contracts
Authority webhook example payload (signed with venue's private key; schema `schema.org/EmergencyEvent` + Aegis extensions):
```json
{
  "specversion": "1.0",
  "type": "ai.aegis.incident.severity_1.created",
  "source": "https://api.aegis.ai/v1/venues/taj-ahmedabad",
  "id": "INC-7741",
  "time": "2026-05-15T02:47:13Z",
  "datacontenttype": "application/json",
  "data": {
    "venue": {...},
    "location": {...},
    "incident": {...},
    "triage": {...},
    "recommended_external_services": ["108", "fire:ahd-central"],
    "media": [{"type": "frame", "signed_url": "..."}, {...}]
  },
  "signature": "ed25519:..."
}
```

---

# PART XIV — CODE QUALITY, TESTING, DEVOPS

## §81. Repo Structure

Monorepo managed with Nx or Turborepo (we'll use **pnpm workspaces + Nx** for polyglot).

```
/
├─ apps/
│  ├─ staff/                     Flutter
│  ├─ responder/                 Flutter
│  ├─ guest-pwa/                 Next.js
│  ├─ dashboard/                 Next.js
│  ├─ authority/                 Next.js
│  └─ marketing/                 Next.js (landing page)
├─ services/
│  ├─ ingest/                    Python FastAPI
│  ├─ vision/                    Python FastAPI
│  ├─ audio/                     Python FastAPI
│  ├─ fusion/                    Python FastAPI
│  ├─ orchestrator/              Python + ADK
│  ├─ dispatch/                  Python FastAPI
│  ├─ triage/                    Python FastAPI (MedGemma wrapper)
│  ├─ evacuation/                Python + networkx
│  ├─ comms/                     Python FastAPI
│  ├─ authority/                 Python FastAPI
│  ├─ venue/                     Python FastAPI
│  ├─ analytics/                 Python FastAPI
│  ├─ audit/                     Python FastAPI
│  ├─ public-api/                Python FastAPI
│  └─ shared/                    Python shared libs (logger, clients, schemas)
├─ agents/
│  ├─ orchestrator/              ADK agent class + prompt
│  ├─ classifier/
│  ├─ cascade/
│  ├─ triage/
│  ├─ dispatcher/
│  ├─ evacuation/
│  ├─ comms/
│  ├─ authority_reporter/
│  └─ post_incident/
├─ packages/
│  ├─ ui_flutter/                Shared Flutter widgets
│  ├─ ui_web/                    Shared React components
│  ├─ api_client_dart/
│  ├─ api_client_ts/
│  └─ schemas/                   Protobuf + JSON Schema (shared contracts)
├─ pubsub-schemas/
├─ prompts/                      All agent prompts (versioned md)
├─ pipelines/                    Vertex AI Pipelines (learning loop, etc.)
├─ terraform/                    IaC for all GCP resources
├─ firebase/                     firestore.rules, firestore.indexes.json, functions/
├─ monitoring/                   dashboards, alerts
├─ docs/
│  ├─ architecture.md
│  ├─ openapi.yaml
│  ├─ runbook.md
│  └─ decisions/                 ADRs
├─ tests/
│  ├─ e2e/                       Playwright + Flutter integration
│  └─ load/                      k6 scripts
├─ .github/workflows/
├─ cloudbuild.yaml               top-level
├─ package.json / pnpm-workspace.yaml
├─ pyproject.toml                Poetry for Python services (uv is faster — pick one)
├─ Makefile                      common dev commands
└─ README.md
```

## §82. Testing Pyramid

- **Unit tests:** pytest for Python (≥70% coverage gate), flutter_test for Dart, vitest for TS. Run on every commit.
- **Contract tests:** Pact or Pydantic-schema-based — every service publishes its input/output schema; consumers test against published schema.
- **Integration tests:** Testcontainers + Firestore emulator + Pub/Sub emulator. Each service has a compose file in `/services/<svc>/tests/docker-compose.yml`.
- **Agent evals:** Bespoke eval harness — 50 canonical scenarios (synthetic + real-from-videos-on-YouTube) where the correct classification/dispatch is known. Runs on every agent change; regression-gates deployment.
- **E2E:** Playwright against the deployed dashboard. Flutter integration_test against a real test venue. Runs nightly + pre-release.
- **Load tests:** k6 scripts in `/tests/load/`. Scenarios: "100 concurrent incidents in one venue", "50 venues active simultaneously". Runs weekly + pre-release.
- **Chaos tests:** Kill a service mid-incident; verify graceful degradation. Runs monthly.

## §83. Code Style + Linting
- **Python:** ruff (lint + format), mypy strict mode. No exceptions.
- **TypeScript:** ESLint + Prettier. Strict TS.
- **Dart:** `dart analyze` + `dart format`. `very_good_analysis` package.
- **SQL:** sqlfluff.
- **Terraform:** tflint + tfsec.
- Pre-commit hooks enforce all of the above.
- Secrets scanner (gitleaks) in pre-commit + CI.

## §84. CI/CD Pipeline (Cloud Build)
```
on: git push to main or PR
pipeline:
  - git checkout + resolve changed paths
  - setup matrix (services, apps) based on changed paths
  - for each affected target in parallel:
    - install deps (cached)
    - lint + format check
    - unit tests (coverage report)
    - build artifact (container or app bundle)
    - security scan (Trivy for containers, OWASP Dependency Check for deps)
    - push to Artifact Registry
  - staging deploy (non-prod Cloud Run services)
  - run smoke tests against staging
  - run E2E subset
  - on main branch only: require manual approval → prod deploy with canary (10% → 50% → 100%)
  - post-deploy: synthetic monitor check
```

## §85. Documentation
- **README at every level.** Runnable quickstart in every service README.
- **Architecture decision records (ADRs)** in `/docs/decisions/` — every non-trivial tech choice has a one-page ADR with context + decision + consequences.
- **Runbook** in `/docs/runbook.md` — oncall guide for real-world operations (even in hackathon context, shipping a runbook screams production-ready to judges).
- **OpenAPI spec** auto-generated from FastAPI services.
- **Prompt registry docs** in `/prompts/README.md`.

## §86. Observability
- **SLOs:** 99.5% availability for Orchestrator (primary critical path), 99% for others.
- **Error budget tracking** in Cloud Monitoring.
- **Synthetic monitors** ping the full flow every 5 minutes.
- **Distributed tracing** on every incident; traces linked from incident detail page.

---

# PART XV — DEVELOPMENT ROADMAP

## §87. Phase 1 — Vertical Slice MVP (by April 24, 2026)

**Goal:** Submit something that passes the Phase 1 bar and telegraphs the ambition.

**Minimum features:**
- One venue (configured via JSON, no UI for onboarding yet)
- One camera feed (RTSP from a public demo URL or a pre-recorded loop)
- Vision Service calling Gemini Flash → classifier output
- Orchestrator with just Classifier + Dispatcher sub-agents
- Dispatch Service with FCM push to a staff device
- Staff Flutter app with: auth, home, incident detail screen, ack action
- Firestore real-time sync
- BigQuery audit append
- Deployed to Cloud Run in asia-south1
- Public demo URL for the staff app
- Public GitHub repo with runnable quickstart
- 2:45 demo video showing end-to-end flow
- Deck (10 slides; §89)

**Architecture explicitly documented in deck, even for parts not built yet** (so judges see the scope).

**Days until deadline:** 2. Assign:
- **Day 1 AM:** Venue config + Firestore schema + auth stub + one Cloud Run (Ingest)
- **Day 1 PM:** Vision Service + Gemini integration + first successful classification
- **Day 2 AM:** Orchestrator + Dispatch + FCM to staff phone
- **Day 2 PM:** Flutter staff app end-to-end + deck + video record
- **Submit by 23:30 buffer.**

## §88. Phase 2 — Product Vault (May 30 – June 9)

The real build-out. After Top 100 selection, you have ~10 days + mentorship + GCP credits.

**New features:**
- All P1 items from §7
- Venue onboarding wizard
- Authority console + webhook
- Cascade predictor
- Triage agent with MedGemma
- Evacuation planner
- Multi-lingual comms (5 languages)
- Learning loop (scaffolded)
- Audit integrity verifier
- Load test showing 50 concurrent incidents
- 3 user-interview write-ups with iteration evidence
- One LOI from a real partner venue
- Updated demo video showing the richer flow
- Rewritten deck with metrics

**Refinement checklist:**
- Every service covered by ≥70% unit tests
- Agent eval harness with 50 scenarios passing
- Observability dashboards published
- Runbook first draft
- ADRs for 5 key decisions

## §89. Phase 3 — Grand Finale (by last week of June)

If selected Top 10, this is polish + pitch.

**New features (stretch, high-ROI for demo):**
- Guest-phone sensor fusion (even mocked is OK, pitch the architecture)
- Crowd-density aware evacuation (real algo, even on synthetic data)
- Predictive risk heatmap
- Fairness dashboard
- Integrity verifier UI

**Pitch artifacts:**
- 3-minute final video
- Live demo runbook
- One-pager leave-behind
- Booth banner (1 image, 1 number, 1 tagline)
- Team name starts with A ✓ (Aegis)

## §90. Post-Hackathon Trajectory (if we win)
- Incorporate company immediately.
- Deploy pilot with the LOI partner within 30 days.
- Apply to Google for Startups Cloud program (Solution Challenge winners get priority).
- Apply to Y Combinator Winter 2027 batch.
- Revenue: ₹25k–₹50k/month/venue subscription; insurance partnership revenue share; enterprise annual contracts ₹5L–₹25L/property.
- 2-year goal: 100 deployed venues, ₹2Cr ARR.

---

# PART XVI — DEMO & PITCH

## §91. 3-Minute Demo Video Shot List

```
0:00–0:10  HOOK: "This is the lobby of the Park Hyderabad,
            2020. At 2:14 AM, a fire starts. In the next 15 minutes,
            17 people will die — most from smoke inhalation that was
            survivable if responders had arrived three minutes earlier."
            (B-roll: stock smoke + timestamps overlaid)

0:10–0:30  PROBLEM: cut to stats — India, 2000+ deaths/yr in venue
            incidents, average dispatch latency 12 min, fragmented
            response. SDG 3 / 11 / 16 badges appear.

0:30–0:45  INTRODUCE AEGIS: one-line pitch. Brand mark.
            "Every second is a life."

0:45–2:15  LIVE DEMO (pre-recorded but real — no Figma):
            - 0:45: Kitchen fire scenario starts. Show frame sampling
                    + Gemini Vision analyzing. Timer begins.
            - 0:55: Classifier output + cascade forecast on screen
            - 1:05: Orchestrator dispatches — show agent trace
                    (judges LOVE seeing the multi-agent graph)
            - 1:15: Priya's phone buzzes, she ack's. 12s elapsed.
            - 1:30: John en route, fire service notified.
            - 1:45: Guest phones in affected rooms receive
                    multi-lingual evacuation cards.
            - 2:00: Fire suppressed. Post-incident report
                    auto-generated. Audit log integrity verified.

2:15–2:40  NOVEL CONTRIBUTIONS: Cascade predictor curve, MedGemma
            triage, fairness dashboard (3 quick flashes).

2:40–2:55  TRACTION: LOI logo. Interview quote from hotel GM.
            Venue-deployed count. Dispatch Latency metric.

2:55–3:00  CALL TO ACTION: "aegis.ai / Better Call Coders."
```

## §92. Grand Finale Live Pitch Script (5 minutes)

**Minute 1 — Hook + Problem (the human)**
Open with Priya's story. 90 seconds.

**Minute 2 — Solution (the what)**
Aegis one-liner. Agent architecture diagram (1 slide, clean). Live demo trigger — fire scenario, timer visible.

**Minute 3 — Demo continues + technical novelty**
Cascade predictor, triage-constrained dispatcher, guest-phone fusion concept. Judges: "we built three things nobody else built."

**Minute 4 — Traction + SDG alignment + business**
LOI, pilot plan, SDG targets (specifically 3.6, 11.5, 16.6). Revenue model.

**Minute 5 — Ask + close**
"We're asking for the pilot funding and partnership. One venue, 30 days, p95 dispatch latency under 60s. If we don't hit it, we refund. The Korean team that won Social Impact in 2025 said the topic is everything. Ours is: every second is a life."

## §93. The One Killer Slide (printed as booth banner)

One image: split-screen. Left = real CCTV still of a hotel fire (stock, publicly available news image). Right = Aegis dispatch screen at T+12s, showing classification + responder en route. Single number: **12 seconds**. Single line: *Every second is a life.* Aegis logo. Team name. QR code to live demo.

---

# PART XVII — VALIDATION & PARTNERSHIPS

## §94. Partner Outreach Plan

### Immediate (pre-Phase-1 submission)
Not possible in 2 days. Skip. Optimize for Phase 2.

### Phase 2 (May 30 – June 9)
Aim for **one** signed LOI from one real venue GM. This is worth ~3 points on Alignment with Cause. Ahmedabad venues to target:
1. The House of MG (boutique heritage hotel, tech-progressive)
2. Taj Skyline Ahmedabad
3. Hyatt Regency Ahmedabad
4. ITC Narmada

Approach: Walk in with a 2-slide deck (cover + architecture diagram), ask for 15 minutes with the GM, not the ops head (GMs decide, ops heads analyze). Pitch: "We're university students building Aegis for Solution Challenge. Not asking for money or commitment — we're asking for 1 hour of your ops team's time to tell us what's broken in your current response, and would you write a 4-sentence statement saying 'we would pilot this' if we nail it?"

Conversion rate: 3–4 walks-ins → 1 LOI. Budget 4 visits.

### Phase 3 (after Top 10)
Expand to wedding-planner association (Gujarat Wedding Planners Network) and one temple trust (Swaminarayan Akshardham media office). These give SDG-11 credibility and the deck story that you're beyond hotels.

## §95. User Interview Protocol (satisfy Google's rubric)

Google's rubric asks for **three specific feedback points from real users with iteration evidence.** Protocol:

**Interview target list:**
- 2 hotel GMs
- 2 hotel duty managers
- 2 hotel security/ops heads
- 1 fire service dispatcher
- 1 108 ambulance coordinator
- 1 wedding planner

**Interview structure (45 min):**
1. 10 min: tell me about a real incident you've handled. What went right, what went wrong?
2. 10 min: show Aegis prototype. Ask them to operate it in a simulated scenario.
3. 15 min: capture specific friction points, unmet needs, surprises.
4. 10 min: willingness-to-pilot / willingness-to-pay.

**Documentation:**
Every interview → a 1-page summary in `/docs/user-research/<date>-<role>.md`. Deck page "What we learned and how we iterated" lists 3 specific changes we made after interviews.

## §96. Pilot Protocol (for the eventual LOI → paid deployment)

**Length:** 30 days.
**Scope:** One venue, 10 cameras, 2 sensors, 5 staff, 2 responders.
**Success criteria:** p95 dispatch latency < 60s during 3 staged drills; zero false-positive-Sev-1s beyond 5 for the month; 95% staff ack rate.
**Cost:** Free for pilot; pricing locked at ₹25k/month if they continue.
**Deliverable at end:** Compliance report, hiring-ready dispatch latency number, testimonial.

---

# CLOSING CHECKLIST — BEFORE PHASE 1 SUBMISSION (April 24)

- [ ] Live MVP URL works on a fresh browser incognito
- [ ] GitHub public, runnable via README quickstart (5-minute setup)
- [ ] Deck: 10 slides, 45s read max, one "agent architecture" slide is killer
- [ ] Demo video: 2:30–2:45, hook in first 10 seconds, live product not Figma
- [ ] SDG mapping in deck: 3.6, 11.5, 16.6 (specific targets, not just numbers)
- [ ] Phase 2 roadmap slide exists so judges see scope of ambition
- [ ] Team name locked: **Aegis** (starts with A)
- [ ] Contact info on deck cover
- [ ] Repo README has architecture diagram
- [ ] License chosen (MIT for SDK packages, Apache 2.0 for the platform code, proprietary for the prompts/fine-tune datasets)
- [ ] .env.example covers every env var
- [ ] CI passes on main
- [ ] One member of the team has walked through the demo end-to-end twice

---

# APPENDIX A — TECH DEPENDENCY MATRIX

| Concern | Tech | Google? |
|---|---|---|
| LLM — reasoning | Gemini 2.5 Pro | ✓ |
| LLM — fast | Gemini 2.5 Flash | ✓ |
| LLM — medical | MedGemma | ✓ |
| Multi-agent runtime | Vertex AI Agent Engine + ADK | ✓ |
| Vector search | Vertex AI Matching Engine | ✓ |
| RAG | Vertex AI Search | ✓ |
| Text embedding | Vertex AI text-embedding-004 | ✓ |
| Training pipelines | Vertex AI Pipelines | ✓ |
| Vision (structured) | Cloud Vision API | ✓ |
| Compute | Cloud Run | ✓ |
| Event bus | Cloud Pub/Sub | ✓ |
| Delayed work | Cloud Tasks | ✓ |
| Cron | Cloud Scheduler | ✓ |
| Live state | Firestore | ✓ |
| Analytics + audit | BigQuery | ✓ |
| Object storage | Cloud Storage | ✓ |
| Relational (if needed) | Cloud SQL | ✓ |
| Cache | Memorystore (Redis) | ✓ |
| Maps | Google Maps Platform (Maps SDK / JS, Routes, Places, Geocoding, Static) | ✓ |
| Push | Firebase Cloud Messaging | ✓ |
| Translation | Cloud Translation | ✓ |
| Text-to-speech | Cloud TTS | ✓ |
| Speech-to-text | Cloud Speech-to-Text | ✓ |
| Auth | Firebase Auth + Identity Platform | ✓ |
| App integrity | Firebase App Check + Play Integrity / App Attest | ✓ |
| Bot protection | reCAPTCHA Enterprise | ✓ |
| Secrets | Secret Manager | ✓ |
| KMS | Cloud KMS | ✓ |
| PII redaction | Cloud DLP | ✓ |
| Edge | Cloud CDN, Cloud Load Balancing, Cloud Armor | ✓ |
| DNS | Cloud DNS | ✓ |
| IAP | Identity-Aware Proxy | ✓ |
| Observability | Cloud Logging, Cloud Trace, Cloud Monitoring, Cloud Profiler, Error Reporting | ✓ |
| CI/CD | Cloud Build + Artifact Registry | ✓ |
| Mobile | Flutter | ✓ |
| Web | Next.js on Cloud Run or Firebase Hosting | ✓ (Firebase) |
| Mobile crash | Firebase Crashlytics | ✓ |
| Mobile perf | Firebase Performance Monitoring | ✓ |
| IaC | Terraform (Google provider) | via official provider |
| IDX (dev env) | Project IDX | ✓ (bonus points for using it) |
| SMS | MSG91 | ✗ (India market) |
| Email | SendGrid | ✗ |

**Google product count integrated deeply: ~30+.** That is the Technical Merit bar being cleared with room to spare.

---

# APPENDIX B — GLOSSARY

- **ADK:** Agent Development Kit (Vertex AI)
- **DL:** Dispatch Latency
- **ESI:** Emergency Severity Index (5 levels; standard in emergency medicine)
- **FPR / FNR:** False Positive / Negative Rate
- **LOI:** Letter of Intent
- **PTT:** Push-to-Talk
- **SAR:** Staff Actioned Rate
- **TTR:** Time To Resolution
- **Sendai Framework:** UN disaster risk reduction framework 2015–2030

---

# APPENDIX C — TEAM ROLE ASSIGNMENTS (suggested for Better Call Coders)

Given team of 4 (Ubaid + 3):
- **Ubaid (tech lead + infra + security):** Cloud infra, auth, RBAC, audit, Pub/Sub, Cloud Run deploys. Author of ADRs.
- **Teammate A (AI / agents lead):** Orchestrator + sub-agents + prompts + eval harness + MedGemma integration.
- **Teammate B (frontend lead):** Flutter staff app + responder app + guest PWA + design system in both ecosystems.
- **Teammate C (data / dashboard / demo lead):** Next.js dashboard + Next.js authority + BigQuery analytics + demo video production + deck.

Daily 15-min sync at 9:30 AM. Async everything else. Every PR needs 1 review + CI green before merge.

---

# FINAL WORD

Winning the Solution Challenge is 80% problem selection + 15% execution + 5% luck. Problem selection is done (§1). This document is the execution blueprint. Every feature in §7 has a priority and a Phase. Every Google service in §15–§22 has an integration pattern. Every screen in §54–§58 has a design contract. Every failure mode has a mitigation.

The only remaining variable is how hard the team is willing to work for nine weeks. Given the track record (OpenEnv, Mentra, WhiteNet), that's not actually a variable.

Ship Phase 1 in 48 hours. Ship Phase 2 in nine days of Product Vault. Ship the pitch of your life at Grand Finale in late June.

*Every second is a life.*
