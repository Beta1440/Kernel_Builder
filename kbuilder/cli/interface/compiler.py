"""Interfaces for compilers."""

import abc

from cement.core.handler import CementBaseHandler


class ICompiler(CementBaseHandler):
    """Interface for managing compilers."""

    class IMeta(abc.ABCMeta):
        label = 'compiler'

    @abc.abstractproperty
    def compiler(self):
        """Current compiler being used."""
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
    def show_compiler(self):
        """Prints the current compiler(s) being used."""
        pass

    @abc.abstractmethod
    def set_compiler(self):
        """Prompts the user as to which compiler(s) to use."""
        pass

    @abc.abstractmethod
    def list_compilers(self):
        """List all detected compilers."""
        pass
