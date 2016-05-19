"""Kernel Builder bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as KbuilderBaseController.

from cement.core import handler
from kbuilder.cli.controllers.base import KbuilderBaseController

def load(app):
    handler.register(KbuilderBaseController)
