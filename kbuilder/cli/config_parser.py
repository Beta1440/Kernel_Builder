"""This module is parses config files. It also dervies a kernel based on
the config file that was parsed.
"""

import os
from os.path import join

from kbuilder.core.arch import Arch
from kbuilder.core.kernel.android import AndroidKernel
from kbuilder.core.kernel.linux import LinuxKernel


def parse_kernel_config(app):
    """Parse a kernel config file."""
    kernel_root = LinuxKernel.find_root(os.getcwd())
    kernel_config_file = join(kernel_root, '.kbuilder.conf')
    kernel_name = str(kernel_root.name)
    app.config.parse_file(kernel_config_file)
    defconfig = app.config.get(kernel_name, 'defconfig')
    arch = Arch[app.config.get(kernel_name, 'arch')]
    kernel = derive_kernel(kernel_root, arch, defconfig)
    app.active_kernel = kernel


def derive_kernel(kernel_root: str, arch: Arch, defconfig: str) -> LinuxKernel:
    """Determine which type of kernel that needs to be created."""
    #  To be implemented later
    return AndroidKernel(kernel_root, arch=arch, defconfig=defconfig)
