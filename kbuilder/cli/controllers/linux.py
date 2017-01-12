"""Provides controllers for Linux."""

from cement.core.controller import CementBaseController, expose


class KbuilderLinuxBuildController(CementBaseController):
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
        self.build_kbuild_image()

    @expose(help='Build a kbuild image',
            aliases=['kernel', 'kbuildimage', 'zImage'],
            aliases_only=True)
    def build_kbuild_image(self):
        """Build a kbuild image."""
        self.builder.build_kbuild_image()

    @expose(help='Default configuration file')
    def defconfig(self):
        """Cross compile a kbuild image."""
        self.builder.build_defconfig()
