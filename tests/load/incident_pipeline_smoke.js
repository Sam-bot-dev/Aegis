import http from "k6/http";
import { check, sleep } from "k6";

const ORCH_BASE_URL = __ENV.ORCH_BASE_URL || "http://localhost:8003";
const VENUE_ID = __ENV.VENUE_ID || "taj-ahmedabad";

export const options = {
  scenarios: {
    incident_spike: {
      executor: "constant-arrival-rate",
      rate: Number(__ENV.INCIDENT_RATE || 5),
      timeUnit: "1s",
      duration: __ENV.DURATION || "30s",
      preAllocatedVUs: Number(__ENV.PRE_ALLOCATED_VUS || 10),
      maxVUs: Number(__ENV.MAX_VUS || 30),
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<1500"],
  },
};

export default function () {
  const zoneIndex = __ITER % 4;
  const isCritical = __ITER % 3 === 0;
  const payload = JSON.stringify({
    venue_id: VENUE_ID,
    zone_id: `load-zone-${zoneIndex}`,
    modality: "VISION",
    category_hint: isCritical ? "FIRE" : "OTHER",
    confidence: isCritical ? 0.93 : 0.34,
  });

  const response = http.post(`${ORCH_BASE_URL}/v1/handle`, payload, {
    headers: { "Content-Type": "application/json" },
    tags: { name: "orchestrator-handle" },
  });

  check(response, {
    "status is 200": (res) => res.status === 200,
    "response has reasoning": (res) => {
      try {
        return Boolean(res.json("reasoning"));
      } catch (_) {
        return false;
      }
    },
  });

  sleep(1);
}
