from cement.core.interface import Interface, validate


def database_validator(klass, obj):
    """Verify that a handler satisfies the IDatabase interface."""
    members = [
        'store',
        'retrieve',
    ]
    validate(IDatabase, obj, members)


class IDatabase(Interface):
    """Database interface."""

    class IMeta:
        label = 'database'
        validator = database_validator

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

    def store(self, item: object, key: str) -> None:
        """Store an item in a data base.

        Args:
            item: The item to store.

        Returns: n/a
        """
        pass

    def retrieve(self, key: str) -> object:
        """Store an item in a data base.

        Args:
            item: The item to store.

        Returns:
            The object at the corresponding key
        """
        pass
