"""GNU C compiler controller"""

from cement.ext.ext_argparse import ArgparseController, expose


class GccController(ArgparseController):
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
        self.show_default_compiler()

    @expose(help='Set default compiler',)
    def set(self):
        """Set the default compiler."""
        self.app.compiler_manager.set_compiler()

    @expose(help='Show the default compiler',)
    def show(self):
        """Show the default compiler."""
        self.app.compiler_manager.show_compiler()

    @expose(help='List all available compilers',)
    def list(self):
        """List all available compilers."""
        self.app.compiler_manager.list_compilers()
