from django.test import TestCase

from plugin.manager import plugin_manager


class TestWhiteboxPluginMap(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginMap"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "Map")

    def test_provides_capabilities(self):
        self.assertEqual(self.plugin.provides_capabilities, ["map"])
