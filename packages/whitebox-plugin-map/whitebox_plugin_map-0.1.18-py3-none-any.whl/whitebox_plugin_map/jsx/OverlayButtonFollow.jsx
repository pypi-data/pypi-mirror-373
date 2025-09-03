const { importWhiteboxComponent } = Whitebox;
import useMapStore from "./stores/map";

const Button = importWhiteboxComponent("ui.button");
const LocationTargetIcon = importWhiteboxComponent("icons.location-target");

const OverlayButtonFollow = () => {
  const isFollowing = useMapStore((state) => state.follow);
  const setFollow = useMapStore((state) => state.setFollow);
  const whiteboxMarkerRef = useMapStore((state) => state.whiteboxMarkerRef);

  // Do not render the button if the marker is not set (no location available)
  if (!whiteboxMarkerRef || !whiteboxMarkerRef.current) {
    return null;
  }

  const iconClassName = isFollowing ? "fill-medium-emphasis" : null;
  const icon = <LocationTargetIcon className={iconClassName} />;

  return (
    <div className="bg-white rounded-2xl h-16 w-16 overflow-hidden flex items-center justify-center">
      <Button
          leftIcon={icon}
          onClick={() => setFollow(true, true)} />
    </div>
  );
}

export {
  OverlayButtonFollow,
};
export default OverlayButtonFollow;
