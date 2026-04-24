#!/usr/bin/env bash
# scripts/dev.sh — start every Aegis Python service locally.
#
# Emulators should already be running (via `make emulators`).
# This script runs each service with uvicorn --reload in a background
# process group, then waits so you can Ctrl-C to kill them all.

set -euo pipefail

cd "$(dirname "$0")/.."

# Pull env vars from .env if present so emulator hosts get picked up.
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi

PIDS=()

trap 'echo; echo ">> Shutting down services..."; for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null || true; done; wait 2>/dev/null || true' EXIT INT TERM

start_service() {
  local name=$1
  local dir=$2
  local port=$3
  echo ">> Starting $name on :$port"
  (
    cd "services/$dir"
    uvicorn main:app --reload --host 0.0.0.0 --port "$port" --log-level info 2>&1 \
      | sed "s/^/[$name] /"
  ) &
  PIDS+=($!)
}

start_service ingest       ingest        8001
start_service vision       vision        8002
start_service orchestrator orchestrator  8003
start_service dispatch     dispatch      8004

echo
echo "========================================================"
echo "  Aegis local dev stack"
echo "--------------------------------------------------------"
echo "  Ingest:       http://localhost:8001/docs"
echo "  Vision:       http://localhost:8002/docs"
echo "  Orchestrator: http://localhost:8003/docs"
echo "  Dispatch:     http://localhost:8004/docs"
echo
echo "  Try the smoke test in another terminal:"
echo "    bash scripts/smoke.sh"
echo
echo "  Press Ctrl-C to stop."
echo "========================================================"

wait
