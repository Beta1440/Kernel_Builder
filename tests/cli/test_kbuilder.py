"""CLI tests for kbuilder."""

from kbuilder.utils import test

class CliTestCase(test.KbuilderTestCase):
    def test_kbuilder_cli(self):
        self.app.setup()
        self.app.run()
        self.app.close()
