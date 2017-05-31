"""Kernel Builder bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as KbuilderBaseController.

from kbuilder.cli.controller.base import KbuilderBaseController
from kbuilder.cli.controller.linux import KbuilderLinuxBuildController
from kbuilder.cli.controller.android import KbuilderAndroidBuildController
from kbuilder.cli.controller.gcc import KbuilderGccController


def load(app):
    app.handler.register(KbuilderBaseController)
    app.handler.register(KbuilderLinuxBuildController)
    app.handler.register(KbuilderAndroidBuildController)
    app.handler.register(KbuilderGccController)

