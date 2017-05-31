"""GNU C compiler controller"""

from cement.ext.ext_argparse import ArgparseController, expose


class KbuilderGccController(ArgparseController):
    class Meta:
        label = 'gcc'
        description = 'Configure local gcc'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['extra_arguments'],
             dict(action='store', nargs='*'))
        ]

    @expose(hide=True)
    def default(self):
        """Build all targets."""
        self.show_default_toolchain()

    @expose(help='Set default toolchain',)
    def set(self):
        """Set the default toolchain."""
        self.app.toolchain_manager.set_toolchain()

    @expose(help='Show the default toolchain',)
    def show(self):
        """Show the default toolchain."""
        self.app.toolchain_manager.show_toolchain()

    @expose(help='List all available toolchains',)
    def list(self):
        """List all available toolchains."""
        self.app.toolchain_manager.list_toolchains()
