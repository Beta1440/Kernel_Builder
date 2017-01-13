"""GNU C compiler controller"""

from cement.core.controller import CementBaseController, expose


class KbuilderGccController(CementBaseController):
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

    @expose(help='Set default toolchain',
            aliases=['set'],
            aliases_only=True)
    def set_default_toolchain(self):
        """Set the default toolchain."""
        self.app.toolchain_manager.set_toolchain()

    @expose(help='Show the default toolchain',
            aliases=['show', 'view'],
            aliases_only=True)
    def show_default_toolchain(self):
        """Display the default toolchain."""
        self.app.toolchain_manager.show_toolchain()

    @expose(help='Lists all available local toolchains',
            aliases=['list'],
            aliases_only=True)
    def list_toolchains(self):
        """Lists all available toolchains."""
        self.app.toolchain_manager.list_toolchains()
