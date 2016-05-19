"""Tests for Example Plugin."""

from kbuilder.utils import test

class ExamplePluginTestCase(test.KbuilderTestCase):
    def test_load_example_plugin(self):
        self.app.setup()
        self.app.plugin.load_plugin('example')
