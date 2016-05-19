"""Kernel Builder base controller."""

from cement.core.controller import CementBaseController, expose

class KbuilderBaseController(CementBaseController):
    class Meta:
        label = 'base'
        description = 'Automate compilling the Linux kernel for android devices'
        arguments = [
            (['-f', '--foo'],
             dict(help='the notorious foo option', dest='foo', action='store',
                  metavar='TEXT') ),
            ]

    @expose(hide=True)
    def default(self):
        print("Inside KbuilderBaseController.default().")

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
