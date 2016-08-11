"""Kernel Builder android controller."""

from cement.core.controller import expose
from .build_linux import KbuilderLinuxBuildController


class KbuilderAndroidBuildController(KbuilderLinuxBuildController):
    """Kernel Builder android controller."""

    class Meta:
        label = 'build'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'Build the Linux kernel for android devices'
        arguments = [(['-t', '--toolchain'],
                      dict(help='The toolchain to use',
                           dest='toolchain',
                           action='store'))
            ]

    def __init__(self, *args, **kw):
        """Init the controller."""
        super().__init__(*args, **kw)
        self.builder = None

    def _setup(self, app):
        """
        See `IController._setup() <#cement.core.cache.IController._setup>`_.
        """
        super()._setup(app)
        self.builder = app.android_builder

    @expose(hide=True)
    def default(self):
        """Build all targets."""
        self.build_ota_package()

    @expose(help='Build an OTA packge', aliases=['otapackage', 'ota'],
            aliases_only=True)
    def build_ota_package(self):
        """Build an OTA packge."""
        self.builder.build_ota_package()
