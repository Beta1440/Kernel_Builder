"""Provides handlers for Gcc toolchains."""

from cement.core.handler import CementBaseHandler
from cement.utils.shell import Prompt
from unipath.path import Path

from kbuilder.cli.interface.toolchain import ToolchainManager
from kbuilder.core import gcc


class GccHandler(ToolchainManager, CementBaseHandler):
    class Meta:
        interface = ToolchainManager
        label = 'gcc_handler'
        description = 'Handler for managing gcc toolchains'

    def __init__(self, **kw_args):
        super().__init__(**kw_args)
        self.toolchain_dir = None
        self.toolchains = None

    def _setup(self, app):
        super()._setup(app)
        self.app = app
        kernel = self.app.active_kernel
        self.toolchain_dir = Path(self.app.config.get(kernel.name, 'toolchain_dir'))
        self.toolchains = gcc.scandir(self.toolchain_dir.expand_user(), kernel.arch)
        self.log = app.log

    @property
    def toolchain(self):
        return self.app.db['default_toolchain']

    def show_toolchain(self) -> None:
        """Display the default toolchain."""
        print(self.app.db['default_toolchain'])

    def list_toolchains(self) -> None:
        toolchain_names = [x.name for x in self.toolchains]
        names = "\n".join(toolchain_names)
        print("Local toolchains:\n\n{}".format(names))

    def set_toolchain(self) -> None:
        prompt = Prompt("Select toolchain", options=self.toolchains, numbered=True)
        toolchain_name = prompt.input
        self.app.db['default_toolchain'] = toolchain_name
        self.log.info("Toolchain set to {}".format(toolchain_name))
