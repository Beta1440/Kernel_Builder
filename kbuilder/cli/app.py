"""Kbuilder CLI app."""

from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults
from kbuilder.cli.interface.database import IDatabase
from kbuilder.cli.handler.shelve import ShelveHandler
from kbuilder.cli.interface.builder_linux import ILinuxBuilder
from kbuilder.cli.handler.builder_linux import LinuxBuilderHandler
from kbuilder.cli.interface.builder_android import IAndroidBuilder
from kbuilder.cli.handler.builder_android import AndroidBuilderHandler
from kbuilder.core.kernel.android import AndroidKernel
from kbuilder.core.kernel.linux import LinuxKernel

from cached_property import cached_property


# Application default.  Should update config/kbuilder.conf to reflect any
# changes, or additions here.
defaults = init_defaults('kbuilder')

# All internal/external plugin configurations are loaded from here
defaults['kbuilder']['plugin_config_dir'] = '/etc/kbuilder/plugins.d'

# External plugins (generally, do not ship with application code)
defaults['kbuilder']['plugin_dir'] = '/var/lib/kbuilder/plugins'

# External templates (generally, do not ship with application code)
defaults['kbuilder']['template_dir'] = '/var/lib/kbuilder/templates'


class KbuilderApp(CementApp):
    class Meta:
        label = 'kbuilder'
        config_defaults = defaults
        define_handlers = [IDatabase,
                           ILinuxBuilder,
                           IAndroidBuilder]

        handlers = [ShelveHandler,
                    LinuxBuilderHandler,
                    AndroidBuilderHandler]

        # All built-in application bootstrapping (always run)
        bootstrap = 'kbuilder.cli.bootstrap'

        # Internal plugins (ship with application code)
        plugin_bootstrap = 'kbuilder.cli.plugins'

        # Internal templates (ship with application code)
        template_module = 'kbuilder.cli.templates'

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
            raise ValueError("Argument must be an instance of LinuxKernel, not {}".format(kernel.__class__))
        self._active_kernel = kernel

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
        builder = self.handler.resolve('android_builder', 'android_builder_handler')
        builder._setup(self)
        return builder

    @cached_property
    def linux_builder(self):
        """Builder for linux targets."""
        builder = self.handler.resolve('linux_builder', 'linux_builder_handler')
        builder._setup(self)
        return builder

    # def setup(self):
    #     super().setup()
    #     self.android_builder._setup(self)
