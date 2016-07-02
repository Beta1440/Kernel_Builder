# Kernel related hooks
import os

from cement.core import hook
from cement.core.kernel import Kernel

def locate_kernel(app):
    kernel = Kernel.find_root(os.getcwd())
    print("kernel located: " + kernel.name)
    app.kernel = kernel
