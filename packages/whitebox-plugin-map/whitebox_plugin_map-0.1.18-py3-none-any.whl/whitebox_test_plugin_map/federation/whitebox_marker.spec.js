import { test } from "@tests/setup";
import { expect } from "@playwright/test";

test.describe("WhiteboxMarker Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");

    // Wait for map to be ready
    const leafletMap = page.locator(".leaflet-container").nth(0);
    await expect(leafletMap).toBeVisible();
  });

  test("should not render marker initially", async ({ page }) => {
    const leafletMap = page.locator(".leaflet-container").nth(0);
    const marker = leafletMap.locator(".leaflet-marker-icon");

    // Marker should not be visible without location data
    await expect(marker).not.toBeVisible();
  });

  test("should render marker after receiving location update", async ({
    page,
  }) => {
    const leafletMap = page.locator(".leaflet-container").nth(0);
    const marker = leafletMap.locator(".leaflet-marker-icon");

    // Initially no marker
    await expect(marker).not.toBeVisible();

    // Send location update
    await page.evaluate(() => {
      const message = {
        type: "location.update",
        location: {
          latitude: 37.7749,
          longitude: -122.4194,
        },
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Marker should now be visible
    await expect(marker).toBeVisible();
  });

  test("should update marker position when location changes", async ({
    page,
  }) => {
    const leafletMap = page.locator(".leaflet-container").nth(0);

    // Send first location
    await page.evaluate(() => {
      const message = {
        type: "location.update",
        location: {
          latitude: 37.7749,
          longitude: -122.4194,
        },
      };
      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    const marker = leafletMap.locator(".leaflet-marker-icon");
    await expect(marker).toBeVisible();

    // Get initial marker position
    const initialPosition = await page.evaluate(() => {
      const markerElement = document.querySelector(".leaflet-marker-icon");
      if (markerElement) {
        return {
          x: markerElement.style.transform || markerElement.style.left,
          y: markerElement.style.transform || markerElement.style.top,
        };
      }
      return null;
    });

    // Send updated location
    await page.evaluate(() => {
      const message = {
        type: "location.update",
        location: {
          latitude: 40.7128,
          longitude: -74.006,
        },
      };
      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Wait for position update
    await page.waitForTimeout(100);

    const updatedPosition = await page.evaluate(() => {
      const markerElement = document.querySelector(".leaflet-marker-icon");
      if (markerElement) {
        return {
          x: markerElement.style.transform || markerElement.style.left,
          y: markerElement.style.transform || markerElement.style.top,
        };
      }
      return null;
    });

    // Position should have changed
    expect(updatedPosition).not.toEqual(initialPosition);
  });
});
