"""Kernel Builder bootstrapping."""

# All built-in application controllers should be imported, and registered
# in this file in the same way as KbuilderBaseController.

from cement.core import handler
from kbuilder.cli.controllers.base import KbuilderBaseController

import os

from cement.core import hook
from kbuilder.core.kernel import Kernel

def locate_kernel(app):
    kernel = Kernel(Kernel.find_root(os.getcwd()))
    print("kernel located: " + kernel.name)
    app.kernel = kernel

def load(app):
    handler.register(KbuilderBaseController)
    hook.register('pre_kernel_compile', locate_kernel)
