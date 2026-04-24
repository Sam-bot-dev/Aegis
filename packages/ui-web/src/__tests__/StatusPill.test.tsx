import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusPill } from "../components/StatusPill";
import { STATUS_COLOR, type IncidentStatus } from "../types";

function hexToRgb(hex: string): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgb(${r}, ${g}, ${b})`;
}

describe("StatusPill", () => {
  it("renders the status token", () => {
    render(<StatusPill status="ACKNOWLEDGED" />);
    expect(screen.getByText("ACKNOWLEDGED")).toBeInTheDocument();
  });

  it("applies a valid border color for every status", () => {
    const statuses = Object.keys(STATUS_COLOR) as IncidentStatus[];
    for (const s of statuses) {
      const { container, unmount } = render(<StatusPill status={s} />);
      const pill = container.firstChild as HTMLElement;
      // jsdom reports border as "1px solid rgb(r, g, b)" — compare via rgb.
      expect(pill.style.border).toContain(hexToRgb(STATUS_COLOR[s]));
      unmount();
    }
  });
});
