"""Stores interfaces for Linux."""

import abc

from cement.core.handler import CementBaseHandler


class LinuxBuilder(CementBaseHandler):
    """Interface for Building linux targets."""

    class IMeta(abc.ABCMeta):
        label = 'linux_builder'

    @abc.abstractproperty
    def kernel(self):
        """Kernel to invoke commands."""
        pass

    @abc.abstractproperty
    def products(self):
        """The completed build targets."""
        pass

    @abc.abstractmethod
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

    @abc.abstractmethod
    def init(self) -> None:
        """Initialize the build enviornment."""
        pass

    @abc.abstractmethod
    def build_kbuild_image(self):
        """Build a compressed kernel image."""
        pass

    @abc.abstractmethod
    def build_defconfig(self):
        """Build the default configuration file."""
        pass
