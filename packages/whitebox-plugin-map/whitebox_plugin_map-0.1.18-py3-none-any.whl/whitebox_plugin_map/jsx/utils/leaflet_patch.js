// Leaflet may also be imported elsewhere (e.g. from the `react-leaflet`), but
// this will ensure that it's loaded before any other Leaflet-related code runs.
// Repeated imports will not cause issues, as the code won't be executed again
import 'leaflet';

// Ensure this is imported to be able to use rotated markers
import 'leaflet-rotatedmarker';

// Import Leaflet CSS to ensure styles are applied
import 'leaflet/dist/leaflet.css';

// Leaflet CSS, when imported, will point to assets by relative URLs. Paths on
// file system do not match the URLs used in the browser, so we need to patch
// the assets to point to the correct URLs.
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import retinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

L.Icon.Default.mergeOptions({
  iconUrl,
  iconRetinaUrl: retinaUrl,
  shadowUrl,
});
