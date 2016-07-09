import os

from kbuilder.core.kernel import Kernel
from unipath import Path

"""Parse config files."""


def parse_android_kernel_config(app):
    """Parse an Android kernel config file."""
    kernel_root = Kernel.find_root(os.getcwd())
    kernel_config_file = str(Path(kernel_root, '.kbuilder.conf'))
    kernel_name = str(kernel_root.name)
    app.config.parse_file(kernel_config_file)
    app.log.info('Parsed config file for ' + kernel_name)
