"""Kernel Builder bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as KbuilderBaseController.

from kbuilder.cli.controllers.base import KbuilderBaseController
from kbuilder.cli.controllers.build_linux import KbuilderLinuxBuildController
from kbuilder.cli.controllers.build_android import KbuilderAndroidBuildController
from kbuilder.cli.controllers.gcc import KbuilderGccController


def load(app):
    app.handler.register(KbuilderBaseController)
    app.handler.register(KbuilderLinuxBuildController)
    app.handler.register(KbuilderAndroidBuildController)
    app.handler.register(KbuilderGccController)

