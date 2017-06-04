"""Provides handlers for Linux."""

from pathlib import Path

from kbuilder.cli.interface.linux import LinuxBuilder


class LinuxBuildHandler(LinuxBuilder):
    class Meta:
        interface = LinuxBuilder
        label = 'linux_build_handler'
        description = 'Handler for building linux targets'

    def __init__(self, **kw_args):
        super().__init__(**kw_args)
        self._kernel = None
        self._db = None
        self.export_path = None
        self.build_log_dir = None
        self._products = []
        self.log = None

    def _setup(self, app):
        super()._setup(app)
        self._kernel = app.active_kernel
        name = self._kernel.name
        self.export_path = Path(app.config.get(name, 'export_dir')).expanduser()
        self.export_path.mkdir(parents=True, exist_ok=True)
        self.build_log_dir = Path(app.config.get(self._kernel.name,
                                                 'log_dir')).expanduser()
        self._db = app.db
        self.log = app.log

    @property
    def kernel(self):
        return self._kernel

    @property
    def products(self):
        return self._products

    @property
    def compiler(self):
        try:
            return self._db['default_compiler']
        except KeyError:
            self.log.warning("Compiler not set")

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

    def init(self) -> None:
        "Initialize the build environment."
        self.kernel.prepare()
