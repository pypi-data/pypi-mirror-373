import { test } from "@tests/setup";
import { expect } from "@playwright/test";

test.describe("Map Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
  });

  test("should render the map container", async ({ page }) => {
    const mapContainer = page.locator(".c_map_area");
    await expect(mapContainer).toBeVisible();
  });

  test("should render Leaflet container", async ({ page }) => {
    const leafletMap = page.locator(".leaflet-container").nth(0);
    await expect(leafletMap).toBeVisible();
  });
});
