import { useEffect } from "react";
import { MapContainer, TileLayer, useMapEvent } from "react-leaflet";
import WhiteboxMarker from "./WhiteboxMarker";
import useMapStore from "./stores/map";

const { SlotLoader } = Whitebox;

const MapSocketInterface = () => {
  // Setup socket events that are not specific to a map contents. Upon unmounting,
  // the event listeners are removed.
  const setWhiteboxCoordinates = useMapStore(
    (state) => state.setWhiteboxCoordinates
  );

  useEffect(() => {
    return Whitebox.sockets.addEventListener("flight", "message", (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "location.update") {
        const location = data.location;
        setWhiteboxCoordinates({
          lat: location.latitude,
          lng: location.longitude,
        });
      }
    });
  }, [setWhiteboxCoordinates]);

  return null;
};

const MapEvents = () => {
  // Setup universal events that are not specific to map contents
  const follow = useMapStore((state) => state.follow);

  useMapEvent("dragstart", () => {
    if (follow) {
      useMapStore.setState({ follow: false });
    }
  });
};

const Map = () => {
  return (
    <MapContainer
      center={[0, 0]}
      zoom={2}
      style={{ width: "100dvw", height: "100%" }}
      data-testid="map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <WhiteboxMarker />
      <SlotLoader name="traffic.markers" />

      <MapSocketInterface />
      <MapEvents />
    </MapContainer>
  );
};

export { Map };
export default Map;
