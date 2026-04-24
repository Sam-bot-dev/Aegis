import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, render, screen } from "@testing-library/react";
import { CountdownRing } from "../components/CountdownRing";

describe("CountdownRing", () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  async function tick(ms: number): Promise<void> {
    await act(async () => {
      await vi.advanceTimersByTimeAsync(ms);
    });
  }

  it("renders the initial remaining count", () => {
    render(<CountdownRing totalSeconds={15} />);
    expect(screen.getByText("15")).toBeInTheDocument();
  });

  it("decrements each second and fires onComplete at zero", async () => {
    const onComplete = vi.fn();
    render(<CountdownRing totalSeconds={3} onComplete={onComplete} />);
    expect(screen.getByText("3")).toBeInTheDocument();

    await tick(1000);
    expect(screen.getByText("2")).toBeInTheDocument();

    await tick(1000);
    expect(screen.getByText("1")).toBeInTheDocument();

    await tick(1000);
    expect(screen.getByText("0")).toBeInTheDocument();

    // Drain the effect that fires onComplete.
    await tick(0);
    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it("resets the remaining counter when totalSeconds changes", async () => {
    // Verify the reset effect without any intermediate tick (keeps the assertion
    // deterministic under fake-timer scheduling, which batches renders).
    const { rerender } = render(<CountdownRing totalSeconds={3} />);
    expect(screen.getByText("3")).toBeInTheDocument();

    rerender(<CountdownRing totalSeconds={10} />);
    await tick(0);
    expect(screen.getByText("10")).toBeInTheDocument();
  });
});
