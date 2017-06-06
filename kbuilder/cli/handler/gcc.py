"""Handlers for compilers."""

from pathlib import Path

from cement.core.handler import CementBaseHandler
from cement.utils.shell import Prompt

from kbuilder.cli.interface.compiler import ICompiler
from kbuilder.core import gcc


class GccHandler(ICompiler, CementBaseHandler):
    """Handler for gcc compilers"""
    class Meta:
        """Cement handler meta information."""
        interface = ICompiler
        label = 'gcc_handler'
        description = 'Handler for managing gcc compilers'

    def __init__(self, **kw_args):
        super().__init__(**kw_args)
        self.compiler_dir = None
        self.compilers = None

    def _setup(self, app):
        super()._setup(app)
        self.app = app
        kernel = self.app.active_kernel
        self.compiler_dir = Path(self.app.config.get('general', 'compiler_dir'))
        self.compilers = gcc.scandir(self.compiler_dir.expanduser(), kernel.arch)
        self.log = app.log

    @property
    def compiler(self):
        return self.app.db['default_compiler']

    def show_compiler(self) -> None:
        """Display the default compiler."""
        print(self.app.db['default_compiler'])

    def list_compilers(self) -> None:
        compiler_names = [x.name for x in self.compilers]
        names = "\n".join(compiler_names)
        print("Local compilers:\n\n{}".format(names))

    def set_compiler(self) -> None:
        prompt = Prompt("Select compiler", options=self.compilers, numbered=True)
        compiler_name = prompt.input
        self.app.db['default_compiler'] = compiler_name
        self.log.info("Compiler set to {}".format(compiler_name))
