"""Linux Build Handler."""

from cement.core.handler import CementBaseHandler
from kbuilder.cli.interface.builder_linux import ILinuxBuilder

from unipath.path import Path

class LinuxBuilderHandler(CementBaseHandler):
    class Meta:
        interface = ILinuxBuilder
        label = 'linux_builder_handler'
        description = 'Handler for building linux targets'

    def __init__(self, **kw_args):
        super().__init__(**kw_args)
        self.kernel = None
        self.base_export_dir = None
        self.export_path = None
        self.build_log_dir = None
        self.products = []
        self.log = None

    def _setup(self, app):
        super()._setup(app)
        self.kernel = app.active_kernel
        name = self.kernel.name
        self.base_export_dir = Path(app.config.get(name, 'export_dir')).expand_user()
        self.export_path = self.base_export_dir.child(self.kernel.version_numbers)
        self.export_path.mkdir(parents=True)
        self.build_log_dir = Path(app.config.get(self.kernel.name,
                                                 'log_dir')).expand_user()
        self.log = app.log

    def build_kbuild_image(self) -> None:
        """Build a kbuild image."""
        self.log.info('Building {0.release_version}'.format(self.kernel))
        self.kernel.arch_clean()
        self.kernel.build_kbuild_image(self.build_log_dir)
        self.log.info('{0.kbuild_image} created'.format(self.kernel))

    def build_defconfig(self):
        """Build a defconfig."""
        self.log.info('making defconfig: ' + self.kernel.defconfig)
        self.kernel.make_defconfig()
