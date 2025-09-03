/* This file creates a Zustand store for managing the state of the map,
 * including the marker coordinates and control settings.
 *
 * The `react-leaflet`'s components are utilized using this state store, meaning
 * that the map and its controls are reactive to the state changes in this store.
 */
import { create } from "zustand";

const createMarkerSlice = (set, get) => ({
  whiteboxMarkerSettings: {
    iconURL: null,
    isRotating: false,
    initialRotation: 0,
  },

  whiteboxCoordinates: null,
  whiteboxMarkerRef: null,

  getWhiteboxCoordinates: () => {
    if (get().whiteboxMarkerRef) {
      return get().whiteboxMarkerRef?.current?.getLatLng();
    } else {
      return get().whiteboxCoordinates;
    }
  },

  setWhiteboxMarkerRef: (ref) => {
    set({
      whiteboxMarkerRef: ref,
    })
    const element = ref.current;

    if (!element) {
      // If the marker got removed, we should also clear the coordinates
      set({ whiteboxCoordinates: null });
      return;
    }

    // Apply marker settings
    get()._applyWhiteboxMarkerSettings();
  },

  setWhiteboxCoordinates: (coordinates) => {
    const prevCoordinates = get().getWhiteboxCoordinates();

    set({ whiteboxCoordinates: coordinates });
    get().markerWhitebox?.setLatLng(coordinates);

    if (!prevCoordinates || !coordinates) return;

    // If the marker is rotating, calculate the bearing and set the rotation angle
    if (get().whiteboxMarkerRef?.current?.options.isRotating) {
      const bearing = get()._calculateBearing(prevCoordinates, coordinates);
      const marker = get().whiteboxMarkerRef.current;
      const initialRotation = marker.options.initialRotation || 0;

      // Adjust the bearing by the initial rotation
      const adjustedBearing = (bearing + initialRotation) % 360;
      marker.setRotationAngle(adjustedBearing);
    }
  },

  setWhiteboxMarkerIcon: ({ iconURL, isRotating = false, initialRotation = 0 }) => {
    set({
      whiteboxMarkerSettings: {
        iconURL,
        isRotating,
        initialRotation,
      },
    });
    get()._applyWhiteboxMarkerSettings();
  },

  // region helpers

  _applyWhiteboxMarkerSettings: () => {
    const settings = get().whiteboxMarkerSettings;

    const markerRef = get().whiteboxMarkerRef;
    const marker = markerRef ? markerRef.current : null;

    if (!marker || !settings.iconURL) return;

    // Create a new icon with the provided URL and options
    const icon = L.icon({
      iconUrl: settings.iconURL,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    });

    // Set the new icon on the marker
    marker.setIcon(icon);

    console.log('== resetting')
    // Reset rotation angle and origin
    marker.setRotationAngle?.(0);
    marker.setRotationOrigin?.("center center");

    // Store rotation options in the marker
    marker.options.isRotating = settings.isRotating;
    marker.options.initialRotation = settings.initialRotation;
  },

  _calculateBearing: (prevLocation, currLocation) => {
    const lat1 = prevLocation.lat * Math.PI / 180;
    const lat2 = currLocation.lat * Math.PI / 180;
    const lng1 = prevLocation.lng * Math.PI / 180;
    const lng2 = currLocation.lng * Math.PI / 180;

    const dLng = lng2 - lng1;
    const y = Math.sin(dLng) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);

    // Calculate the angle in radians
    let bearing = Math.atan2(y, x);

    // Convert to degrees and normalize to [0, 360]
    bearing = (bearing * 180 / Math.PI + 360) % 360;

    return bearing;
  },

  // endregion helpers
});

const createControlSlice = (set) => ({
  defaultFollowZoom: 12,

  follow: true,
  followShouldZoomIn: false,

  setFollow: (follow, followShouldZoomIn) => {
    set({
      follow,
      followShouldZoomIn: !!followShouldZoomIn,
    });
  },
});

const useMapStore = create((...a) => ({
  ...createMarkerSlice(...a),
  ...createControlSlice(...a),
}));

export default useMapStore;
