"""Kbuilder CLI app."""

from cached_property import cached_property
from cement.core.foundation import CementApp
from cement.ext.ext_colorlog import ColorLogHandler
from cement.utils.misc import init_defaults

from kbuilder.cli.handler.android import AndroidBuildHandler
from kbuilder.cli.handler.gcc import GccHandler
from kbuilder.cli.handler.linux import LinuxBuildHandler
from kbuilder.cli.handler.shelve import ShelveHandler
from kbuilder.cli.interface.android import AndroidBuilder
from kbuilder.cli.interface.database import Database
from kbuilder.cli.interface.linux import LinuxBuilder
from kbuilder.cli.interface.compiler import CompilerManager
from kbuilder.core.kernel.android import AndroidKernel
from kbuilder.core.kernel.linux import LinuxKernel

COLORS = {
    'DEBUG':    'cyan',
    'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red,bg_white',
}

# Application default.  Should update config/kbuilder.conf to reflect any
# changes, or additions here.
defaults = init_defaults('kbuilder')

# All internal/external plugin configurations are loaded from here
defaults['kbuilder']['plugin_config_dir'] = '/etc/kbuilder/plugins.d'

# External plugins (generally, do not ship with application code)
defaults['kbuilder']['plugin_dir'] = '/var/lib/kbuilder/plugins'

# External templates (generally, do not ship with application code)
defaults['kbuilder']['template_dir'] = '/var/lib/kbuilder/templates'


class App(CementApp):
    class Meta:
        label = 'kbuilder'
        config_defaults = defaults
        define_handlers = [Database,
                           CompilerManager,
                           LinuxBuilder,
                           AndroidBuilder]

        handlers = [ShelveHandler,
                    GccHandler,
                    LinuxBuildHandler,
                    AndroidBuildHandler]

        # All built-in application bootstrapping (always run)
        bootstrap = 'kbuilder.cli.bootstrap'

        # Internal plugins (ship with application code)
        plugin_bootstrap = 'kbuilder.cli.plugins'

        # Internal templates (ship with application code)
        template_module = 'kbuilder.cli.templates'

        log_handler = ColorLogHandler(colors=COLORS)

    def __init__(self, label=None, **kw):
        super().__init__(**kw)
        self._active_kernel = None

    @cached_property
    def db(self):
        """Database of app."""
        db = self.handler.resolve('database', 'shelve_handler')
        db._setup(self)
        return db

    @property
    def active_kernel(self):
        """The kernel being acted upon."""
        return self._active_kernel

    @active_kernel.setter
    def active_kernel(self, kernel: LinuxKernel):
        """Set the active kernel to a new kernel."""
        if not isinstance(kernel, LinuxKernel):
            raise ValueError("Argument must be an instance of LinuxKernel, not {}".format(
                    kernel.__class__))
        self._active_kernel = kernel

    @cached_property
    def compiler_manager(self):
        manager = self.handler.resolve('compiler', 'gcc_handler')
        manager._setup(self)
        return manager

    @property
    def builder(self):
        """Builder for the current kernel."""
        if isinstance(self.active_kernel, AndroidKernel):
            return self.android_builder
        else:
            return self.linux_builder

    @cached_property
    def android_builder(self):
        """Builder for android targets."""
        builder = self.handler.resolve('android_builder', 'android_build_handler')
        builder._setup(self)
        return builder

    @cached_property
    def linux_builder(self):
        """Builder for linux targets."""
        builder = self.handler.resolve('linux_builder', 'linux_build_handler')
        builder._setup(self)
        return builder
