"""Testing utilities for Kernel Builder."""

from kbuilder.cli.main import KbuilderTestApp
from cement.utils.test import *

class KbuilderTestCase(CementTestCase):
    app_class = KbuilderTestApp

    def setUp(self):
        """Override setup actions (for every test)."""
        super(KbuilderTestCase, self).setUp()

    def tearDown(self):
        """Override teardown actions (for every test)."""
        super(KbuilderTestCase, self).tearDown()

