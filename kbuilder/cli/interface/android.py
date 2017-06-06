"""Interfaces for Android."""

import abc

from .linux import ILinuxBuild


class IAndroidBuild(ILinuxBuild):
    """Interface for Building android targets."""

    class IMeta(abc.ABCMeta):
        label = 'android_build'

    @abc.abstractproperty
    def compiler(self):
        """The cross compiler to use in building the kernel."""
        pass

    @abc.abstractmethod
    def _setup(self, app):
        """ Set up the app and compiler.

        The setup function is called during application initialization and
        must 'setup' the handler object making it ready for the framework
        or the application to make further calls to it.

        Args:
            app:
                The application object.

        Returns: n/a

        """
        pass

    @abc.abstractmethod
    def build_boot_img(self):
        """Build a boot.img."""
        pass

    @abc.abstractmethod
    def build_ota_package(self):
        """Build an OTA package."""
        pass
