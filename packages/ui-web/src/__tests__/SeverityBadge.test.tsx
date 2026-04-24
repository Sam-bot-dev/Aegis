import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { SeverityBadge } from "../components/SeverityBadge";
import { SEVERITY_COLOR } from "../types";

function hexToRgb(hex: string): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  return `rgb(${r}, ${g}, ${b})`;
}

describe("SeverityBadge", () => {
  it("renders the severity label for each severity", () => {
    const severities = ["S1", "S2", "S3", "S4"] as const;
    for (const s of severities) {
      const { unmount } = render(<SeverityBadge severity={s} />);
      expect(screen.getByText(new RegExp(`^${s}`))).toBeInTheDocument();
      unmount();
    }
  });

  it("uses the blueprint color token for each severity", () => {
    for (const s of ["S1", "S2", "S3", "S4"] as const) {
      const { container, unmount } = render(<SeverityBadge severity={s} />);
      const pill = container.firstChild as HTMLElement;
      expect(pill.style.background).toBe(hexToRgb(SEVERITY_COLOR[s]));
      unmount();
    }
  });
});
