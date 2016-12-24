"""Kernel Builder base controller."""

from cement.core.controller import CementBaseController, expose


VERSION = '0.1.0'

BANNER = """
Kernel Builder {}
Copyright (c) 2016 Dela Anthonio
""".format(VERSION)


class KbuilderBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'Automate compilling the Linux kernel '
        arguments = [
            (['-j', '--jobs'],
             dict(help='the amount of jobs to build with', dest='jobs',
                  action='store')),
            (['-v', '--version'],
             dict(version=BANNER,
                  action='version'))
            ]

    @expose(hide=True)
    def default(self):
        """Build all targets """
        pass

    @expose(help='Remove build files in the arch directory',
            aliases=['archclean'], aliases_only=True)
    def arch_clean(self):
        """Print the kernel linux version."""
        self.app.log.info('Cleaning arch specific files')
        self.app.active_kernel.arch_clean()

    @expose(help='Remove build files')
    def clean(self):
        """Clean build files."""
        self.app.log.info('Cleaning build files')
        self.app.active_kernel.clean()

    @expose(help='Print the kernel Linux version',
            aliases=['linuxversion', 'version'],
            aliases_only=True)
    def linux_version(self):
        """Print the kernel linux version."""
        print(self.app.active_kernel.linux_version)

    @expose(help='Print the kernel release version',
            aliases=['releaseversion', 'release'],
            aliases_only=True)
    def release_version(self):
        """Print the kernel release version."""
        print(self.app.active_kernel.release_version)

    @expose(help='Print the kernel local version',
            aliases=['localversion', 'local'],
            aliases_only=True)
    def local_version(self):
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
