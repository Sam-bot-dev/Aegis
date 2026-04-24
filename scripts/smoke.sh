#!/usr/bin/env bash
# scripts/smoke.sh — drive Aegis end-to-end locally.
#
# Flow:
#   1. Hit every service's /health
#   2. Send a frame to Ingest
#   3. Ask Vision to classify a "fire" byte
#   4. Send the signal to Orchestrator → should dispatch
#   5. Walk a dispatch through the ack/enroute/arrived state machine

set -euo pipefail

INGEST="${INGEST_SERVICE_URL:-http://localhost:8001}"
VISION="${VISION_SERVICE_URL:-http://localhost:8002}"
ORCH="${ORCHESTRATOR_SERVICE_URL:-http://localhost:8003}"
DISP="${DISPATCH_SERVICE_URL:-http://localhost:8004}"

bold()  { printf "\n\033[1;36m== %s ==\033[0m\n" "$*"; }
ok()    { printf "  \033[32m✓\033[0m %s\n" "$*"; }
fail()  { printf "  \033[31m✗\033[0m %s\n" "$*"; exit 1; }

bold "1/5  Health checks"
for url in "$INGEST/health" "$VISION/health" "$ORCH/health" "$DISP/health"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  if [ "$code" = "200" ]; then ok "$url"; else fail "$url → HTTP $code"; fi
done

bold "2/5  Frame ingest"
# Tiny bytes that look like a JPEG (not real image, but enough for the stub path).
tmp=$(mktemp)
printf '\xff\xd8\xff\xe0%.0s' {1..200} > "$tmp"
INGEST_RESP=$(curl -s -X POST "$INGEST/v1/frames" \
  -F "venue_id=taj-ahmedabad" \
  -F "camera_id=K-12" \
  -F "frame=@$tmp;type=image/jpeg")
rm -f "$tmp"
echo "  response: $INGEST_RESP"
echo "$INGEST_RESP" | grep -q '"frame_id"' && ok "ingest accepted" || fail "ingest did not return frame_id"

bold "3/5  Vision classify (stub)"
# first byte 0x00 → FIRE in the phase-1 stub
FRAME_B64=$(python -c "import base64; print(base64.b64encode(b'\\x00'+b'\\xff'*512).decode())")
VISION_RESP=$(curl -s -X POST "$VISION/v1/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"venue_id\":\"taj-ahmedabad\",\"camera_id\":\"K-12\",\"zone_id\":\"kitchen-main\",\"frame_base64\":\"$FRAME_B64\"}")
echo "  response: $VISION_RESP"
CAT=$(echo "$VISION_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['signal']['category_hint'])")
[ "$CAT" = "FIRE" ] && ok "vision classified FIRE" || fail "vision returned $CAT, expected FIRE"

bold "4/5  Orchestrator handle"
ORCH_RESP=$(curl -s -X POST "$ORCH/v1/handle" \
  -H "Content-Type: application/json" \
  -d '{"venue_id":"taj-ahmedabad","zone_id":"kitchen-main","modality":"VISION","category_hint":"FIRE","confidence":0.9}')
echo "  response: $ORCH_RESP"
SEV=$(echo "$ORCH_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['classification']['severity'])")
DISPATCHED=$(echo "$ORCH_RESP" | python -c "import sys,json; print(json.load(sys.stdin)['dispatched'])")
[ "$SEV" = "S2" ] && ok "classified S2"     || fail "expected S2 got $SEV"
[ "$DISPATCHED" = "True" ] && ok "dispatched" || fail "expected dispatch"

bold "5/5  Dispatch state machine"
DID="DSP-smoke-001"
for action in ack enroute arrived; do
  R=$(curl -s -X POST "$DISP/v1/dispatches/$DID/$action")
  STATUS=$(echo "$R" | python -c "import sys,json; print(json.load(sys.stdin)['status'])")
  ok "$action → $STATUS"
done

bold "Done"
echo "  All systems nominal. You just ran the full Aegis pipeline."
