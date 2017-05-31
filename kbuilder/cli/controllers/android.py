"""Provides controllers for Android."""

from cement.ext.ext_argparse import ArgparseController, expose


class KbuilderAndroidBuildController(ArgparseController):
    """Kernel Builder android controller."""

    class Meta:
        label = 'android_build'
        stacked_on = 'build'
        stacked_type = 'embedded'
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
        self.builder = app.builder

    @expose(help='Build an OTA packge', aliases=['ota'],)
    def otapackage(self):
        """Build an OTA packge."""
        self.builder.build_ota_package()
