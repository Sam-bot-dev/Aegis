# `services/dispatch`

Owns the responder paging and acknowledgement state machine. Consumes
`dispatch-events` and tracks each dispatch through:

```
PAGED → ACKNOWLEDGED → EN_ROUTE → ARRIVED → HANDED_OFF
                   ↓
              TIMED_OUT → auto-escalation
```

## Endpoints

| Method | Path                              | Role                     |
| ------ | --------------------------------- | ------------------------ |
| GET    | /health                           | liveness                 |
| POST   | /v1/dispatches/{id}/ack           | responder acknowledges   |
| POST   | /v1/dispatches/{id}/enroute       | responder moving         |
| POST   | /v1/dispatches/{id}/arrived       | on scene                 |
| GET    | /v1/dispatches/{id}               | current state            |

## Phase 1 vs Phase 2

- **Phase 1:** state in-process (`_STATE` dict). Fine for the demo.
- **Phase 2:** state in Firestore, FCM push replaces log statements,
  15-second escalation via Cloud Tasks.

## Run

```bash
make dispatch   # :8004
```
