"""Kernel Builder base controller."""

from cement.core.controller import CementBaseController, expose
from kbuilder.core import kbuilder

VERSION = '0.1.0'

BANNER = """
Kernel Builder {}
Copyright (c) 2016 Dela Anthonio
""".format(VERSION)

class KbuilderBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'Automate compilling the Linux kernel for android devices'
        arguments = [
            (['-c', '--clean'],
             dict(help='execute make clean before each build', dest='clean',
                  action='store_true')),
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
        kbuilder.main()

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
