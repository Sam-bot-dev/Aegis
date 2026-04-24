import { expect, test } from "@playwright/test";

const DASHBOARD_URL = process.env.DASHBOARD_URL || "http://127.0.0.1:3002";

test("dashboard renders the command board shell", async ({ page }) => {
  await page.goto(DASHBOARD_URL);

  await expect(page.getByText("Venue dashboard")).toBeVisible();
  await expect(page.getByText("AEGIS · CONTROL ROOM")).toBeVisible();
});
