# Pub/Sub schemas

Every topic published by Aegis has a schema file in this directory. Publishers
validate outgoing messages against the schema; subscribers validate incoming.
This prevents silent schema drift — a common source of production bugs in
event-driven systems.

## Topics

| Topic                 | Producer                  | Consumers                                 | Schema                           |
| --------------------- | ------------------------- | ----------------------------------------- | -------------------------------- |
| `raw-frames`          | Ingest / Edge Gateway     | Vision                                    | [`raw_frame.schema.json`](./raw_frame.schema.json) |
| `audio-chunks`        | Ingest                    | Audio                                     | `audio_chunk.schema.json` (P2)   |
| `sensor-events`       | Ingest                    | Fusion                                    | [`sensor_event.schema.json`](./sensor_event.schema.json) |
| `perceptual-signals`  | Vision / Audio / Fusion   | Orchestrator                              | [`perceptual_signal.schema.json`](./perceptual_signal.schema.json) |
| `incident-events`     | Orchestrator              | Dispatch, Audit, UI subscribers           | [`incident_event.schema.json`](./incident_event.schema.json) |
| `dispatch-events`     | Orchestrator / Dispatch   | Staff / Responder apps (via FCM), Audit   | [`dispatch_event.schema.json`](./dispatch_event.schema.json) |
| `audit-events`        | All services              | BigQuery sink                             | `audit_event.schema.json` (P2)   |

## Ordering keys

| Topic                 | Ordering key                    | Why                                     |
| --------------------- | ------------------------------- | --------------------------------------- |
| `raw-frames`          | `venue_id:camera_id`            | Per-camera frames in order              |
| `sensor-events`       | `venue_id:sensor_id`            | Per-sensor readings in order            |
| `perceptual-signals`  | `venue_id`                      | Same-venue signals processed in order   |
| `incident-events`     | `venue_id:incident_id`          | Per-incident transitions strictly ordered |
| `dispatch-events`     | `venue_id:incident_id`          | Same                                      |

## Notes

- `raw-frames` may include an optional `zone_id` when the ingest caller already
  knows which venue zone the camera maps to. The Vision subscriber uses that if
  present, otherwise it falls back to `camera_id`.
