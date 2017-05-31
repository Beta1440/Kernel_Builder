"""Provides controllers for Linux."""

from cement.ext.ext_argparse import ArgparseController, expose


class LinuxBuildController(ArgparseController):
    """Kernel Builder Linux build controller."""

    class Meta:
        label = 'build'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'Build the Linux kernel'
        arguments = []

    def __init__(self, *args, **kw):
        """Init the controller."""
        super().__init__(*args, **kw)
        self.builder = None

    def _setup(self, app):
        """Initialize instance variables of controller.

        See `IController._setup() <#cement.core.cache.IController._setup>`_.
        """
        super()._setup(app)
        self.builder = app.builder

    @expose(help='Build a kbuild image')
    def default(self):
        """Build all targets."""
        self.kernel()

    @expose(help='Build a kbuild image',
            aliases=['kbuildimage', 'zimage'],)
    def kernel(self):
        """Build a kernel image."""
        self.builder.build_kbuild_image()

    @expose(help='Build a default configuration file')
    def defconfig(self):
        """Build a default configuration file."""
        self.builder.build_defconfig()
