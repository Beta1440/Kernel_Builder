"""Kernel Builder base controller."""

from cement.ext.ext_argparse import ArgparseController, expose

VERSION = '0.1.0'

BANNER = """
Kernel Builder {}
Copyright (c) 2016 Dela Anthonio
""".format(VERSION)


class KbuilderBaseController(ArgparseController):
    class Meta:
        label = 'base'
        description = 'Automate compilling the Linux kernel '
        arguments = [
            (['-j', '--jobs'],
             dict(help='the amount of jobs to build with', dest='jobs',
                  action='store')),
            (['-v', '--version'],
             dict(version=BANNER,
                  action='version')),
            (['extra_arguments'],
             dict(action='store', nargs='*'))
        ]
        parser_options = {}

    @expose(hide=True)
    def default(self):
        """Build all targets """
        pass

    @expose(help='Remove build files in the arch directory',)
    def archclean(self):
        """Print the kernel linux version."""
        self.app.log.info('Cleaning arch specific files')
        self.app.active_kernel.arch_clean()

    @expose(help='Remove build files')
    def clean(self):
        """Clean build files."""
        self.app.log.info('Cleaning build files')
        self.app.active_kernel.clean()

    @expose(help='Initialize the build environment')
    def init(self):
        """Initialize the build environment files."""
        self.app.log.info('Initializing the build environment')
        self.app.toolchain_manager.set_toolchain()
        self.app.builder.init()

    @expose(help='Print the kernel Linux version',)
    def linuxversion(self):
        """Print the kernel linux version."""
        print(self.app.active_kernel.linux_version)

    @expose(help='Print the kernel release version',)
    def releaseversion(self):
        """Print the kernel release version."""
        print(self.app.active_kernel.release_version)

    @expose(help='Print the kernel local version')
    def localversion(self):
        """Print the kernel local version."""
        print(self.app.active_kernel.local_version)


        # If using an output handler such as 'mustache', you could also
        # render a data dictionary using a template.  For example:
        #
        #   data = dict(foo='bar')
        #   self.app.render(data, 'default.mustache')
        #
        #
        # The 'default.mustache' file would be loaded from
        # ``kbuilder.cli.templates``, or ``/var/lib/kbuilder/templates/``.
        #
