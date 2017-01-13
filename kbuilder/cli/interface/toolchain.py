"""Provides interfaces for Toolchains."""

import abc


class ToolchainManager(object):
    """Interface for managing toolchains."""

    class IMeta(abc.ABCMeta):
        label = 'toolchain'

    @abc.abstractproperty
    def toolchain(self):
        """Current toolchain being used."""
        pass

    @abc.abstractmethod
    def _setup(self, app):
        """
        The setup function is called during application initialization and
        must 'setup' the handler object making it ready for the framework
        or the application to make further calls to it.

        Args:
            app: The application object.

        Returns: n/a

        """
        pass

    @abc.abstractmethod
    def show_toolchain(self):
        """Prints the current toolchain(s) being used."""
        pass

    @abc.abstractmethod
    def set_toolchain(self):
        """Prompts the user as to which toolchain(s) to use."""
        pass

    @abc.abstractmethod
    def list_toolchains(self):
        """List all detected toolchains."""
        pass
