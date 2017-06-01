"""Testing utilities for Kernel Builder."""

from cement.utils.test import *

from kbuilder.cli.main import TestApp


class TestCase(CementTestCase):
    app_class = TestApp

    def setUp(self):
        """Override setup actions (for every test)."""
        super(TestCase, self).setUp()

    def tearDown(self):
        """Override teardown actions (for every test)."""
        super(TestCase, self).tearDown()
