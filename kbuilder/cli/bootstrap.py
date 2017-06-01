"""Kernel Builder bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as BaseController.

from kbuilder.cli.controller.android import AndroidBuildController
from kbuilder.cli.controller.base import BaseController
from kbuilder.cli.controller.gcc import GccController
from kbuilder.cli.controller.linux import LinuxBuildController


def load(app):
    app.handler.register(BaseController)
    app.handler.register(LinuxBuildController)
    app.handler.register(AndroidBuildController)
    app.handler.register(GccController)
