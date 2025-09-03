from whitebox import Plugin


class WhiteboxPluginMap(Plugin):
    """
    A plugin that displays a map using leaflet.js and updates the map with the
    GPS data received from the GPS plugin.

    Attributes:
        name: The name of the plugin.
        plugin_template: Path to the plugin's template.
        plugin_css: List of paths to the plugin's CSS files.
        plugin_js: List of paths to the plugin's JS files.
    """

    name = "Map"

    provides_capabilities = ["map"]
    slot_component_map = {
        "map.display": "Map",
        "map.overlay-button-follow": "OverlayButtonFollow",
    }
    state_store_map = {
        "map": "stores/map",
    }


plugin_class = WhiteboxPluginMap
