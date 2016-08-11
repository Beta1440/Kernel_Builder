"""GNU C compiler controller"""

from cement.core.controller import CementBaseController, expose

from kbuilder.core import gcc
from kbuilder.core.gcc import Toolchain
from unipath.path import Path


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
        kernel = self.app.active_kernel
        toolchain_dir = Path(self.app.config.get(kernel.name, 'toolchain_dir'))
        toolchains = gcc.scandir(toolchain_dir.expand_user(), kernel.arch)

        try:
            toolchain_name = self.app.pargs.extra_arguments[0]
            toolchain = Toolchain.find(toolchains, toolchain_name)

        except IndexError:
            toolchain = gcc.prompt_one(toolchains)

        self.app.db.store(toolchain, 'default_toolchain')

    @expose(help='Show the default toolchain',
            aliases=['show', 'view'],
            aliases_only=True)
    def show_default_toolchain(self):
        """Display the default toolchain."""
        print(self.app.db.retrieve('default_toolchain'))
