"""Provides interfaces for Android."""

from cement.core.interface import Attribute, validate
from .linux import LinuxBuilder


def android_builder_validator(klass, obj):
    """Verify that a handler satisfies the AndroidBuilder interface."""
    members = [
        'toolchain',
        '_setup',
        'build_boot_image',
        'build_ota_package'
    ]
    validate(AndroidBuilder, obj, members)


class AndroidBuilder(LinuxBuilder):
    """Interface for Building android targets."""

    class IMeta:
        label = 'android_builder'
        validator = android_builder_validator

    toolchain = Attribute('The cross compiler to use in building the kernel')

    def _setup(self, app):
        """ Set up the app and toolchain.

        The setup function is called during application initialization and
        must 'setup' the handler object making it ready for the framework
        or the application to make further calls to it.

        Args:
            app:
                The application object.

        Returns: n/a

        """
        pass

    def build_boot_img(self):
        """Build a boot.img."""
        pass

    def build_ota_package(self):
        """Build an OTA package."""
        pass
