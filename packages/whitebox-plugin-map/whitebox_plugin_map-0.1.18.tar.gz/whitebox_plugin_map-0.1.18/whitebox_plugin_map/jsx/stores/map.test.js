import useMapStore from "./map";

describe("useMapStore", () => {
  test("should have correct initial state", () => {
    const state = useMapStore.getState();

    expect(state.whiteboxMarkerSettings).toEqual({
      iconURL: null,
      isRotating: false,
      initialRotation: 0,
    });

    expect(state.whiteboxCoordinates).toBeNull();
    expect(state.whiteboxMarkerRef).toBeNull();

    expect(state.defaultFollowZoom).toBe(12);
    expect(state.follow).toBe(true);
  });

  test("should have all required methods", () => {
    const state = useMapStore.getState();

    expect(typeof state.setWhiteboxCoordinates).toBe("function");
    expect(typeof state.setFollow).toBe("function");
  });
});

describe("Marker Slice", () => {
  describe("setWhiteboxCoordinates", () => {
    test("should set whitebox coordinates from null", () => {
      const { setWhiteboxCoordinates } = useMapStore.getState();

      const coordinates = { lat: 37.7749, lon: -122.4194 };
      setWhiteboxCoordinates(coordinates);

      const state = useMapStore.getState();
      expect(state.whiteboxCoordinates).toEqual(coordinates);
    });

    test("should update existing whitebox coordinates", () => {
      const { setWhiteboxCoordinates } = useMapStore.getState();

      // Set initial coordinates
      const initialCoords = { lat: 37.7749, lon: -122.4194 };
      setWhiteboxCoordinates(initialCoords);

      // Update coordinates
      const newCoords = { lat: 40.7128, lon: -74.006 };
      setWhiteboxCoordinates(newCoords);

      const state = useMapStore.getState();
      expect(state.whiteboxCoordinates).toEqual(newCoords);
      expect(state.whiteboxCoordinates).not.toEqual(initialCoords);
    });
  });
});

describe("Control Slice", () => {
  describe("defaultFollowZoom", () => {
    test("should have correct default follow zoom", () => {
      const state = useMapStore.getState();
      expect(state.defaultFollowZoom).toBe(12);
    });

    test("should allow manual override of defaultFollowZoom", () => {
      // Test that we can manually set this value if needed
      useMapStore.setState({ defaultFollowZoom: 15 });

      const state = useMapStore.getState();
      expect(state.defaultFollowZoom).toBe(15);
    });
  });

  describe("follow state", () => {
    test("should start with follow enabled", () => {
      const state = useMapStore.getState();
      expect(state.follow).toBe(true);
    });
  });

  describe("setFollow", () => {
    test("should enable follow mode", () => {
      const { setFollow } = useMapStore.getState();

      // Start with follow disabled
      useMapStore.setState({ follow: false });

      setFollow(true);

      const state = useMapStore.getState();
      expect(state.follow).toBe(true);
    });

    test("should disable follow mode", () => {
      const { setFollow } = useMapStore.getState();

      // Start with follow enabled (default)
      setFollow(false);

      const state = useMapStore.getState();
      expect(state.follow).toBe(false);
    });
  });
});
