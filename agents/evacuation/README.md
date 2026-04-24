# Evacuation Agent

Computes evacuation routes per affected zone. **Fifth of the five novel
contributions** (blueprint §63).

Not shortest-path — **flow-balanced** routing using min-cost max-flow
over the indoor graph. Industry-standard in real evacuation engineering,
but nobody else in the Solution Challenge will have built it.

**Model:** `gemini-2.5-pro` (routing narrative + dynamic re-plan) + a
           pure Python solver (networkx + custom)
**Tools:** `indoor_graph`, `zone_density`, `maps_routes_outdoor`

## Why flow-balanced instead of shortest-path

Shortest-path routes every guest to the nearest exit → guarantees a
bottleneck at that exit. Flow-balanced routes minimize
`max_e (flow_e / capacity_e)` across all edges, which spreads egress
across multiple exits. This is a real, published technique in
evacuation literature; it's just that no one in our competition will
have implemented it.

## Phase 1

Not built. Phase 1 evacuation plan is a static "head for the nearest
marked exit" message.

## Phase 2 build order

1. Indoor graph model: zones = nodes, corridors = edges with attrs
   `(length_m, width_m, max_pax_per_min, accessible, stairs_count)`
2. Min-cost max-flow solver (networkx has it; wrap for our schema)
3. Per-guest card generation (takes guest's current zone → returns a
   personalised route)
4. Real-time re-plan triggered by staff "corridor blocked" tap or
   density spike
5. Outdoor leg via Google Maps Routes API

## Demo path

Use a small synthetic venue (8 zones, 12 edges). Show the
shortest-path route creating a bottleneck, then show flow-balanced
dispersing egress. This is a killer deck slide.
