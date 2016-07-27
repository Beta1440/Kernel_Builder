from cement.core.interface import Interface, Attribute, validate


def linux_builder_validator(klass, obj):
    """Verify that a handler satisfies the ILinuxBuilder interface."""
    members = [
        'kernel',
        'products',
        '_setup',
        'build_kbuild_image',
        'build_defconfig',
        ]
    validate(ILinuxBuilder, obj, members)


class ILinuxBuilder(Interface):
    """Interface for Building linux targets."""

    class IMeta:
        label = 'linux_builder'
        validator = linux_builder_validator

    kernel = Attribute('Kernel to invoke commands')

    products = Attribute('The completed build targets')

    def _setup(self, app):
        """
        The setup function is called during application initialization and
        must 'setup' the handler object making it ready for the framework
        or the application to make further calls to it.

        Args:
            app:
                The application object.

        Returns: n/a

        """
        pass

    def build_kbuild_image(self):
        """Build a compressed kernel image."""
        pass

    def build_defconfig(self):
        """Bulid the default configuration file."""
        pass