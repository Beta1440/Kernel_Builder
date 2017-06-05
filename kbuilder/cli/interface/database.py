"""Interfaces for modules which provide persistent storage."""

from cement.core.interface import Interface, validate


def database_validator(klass, obj):
    """Verify that a handler satisfies the Database interface."""
    members = [
        '__setitem__',
        '__getitem__',
    ]
    validate(Database, obj, members)


class Database(Interface):
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

    def __setitem__(self, key: str, value: object) -> object:
        """Store an item in a data base.

        Args:
            key: the key to use to retrieve the item
            item: The item to store.

        Returns: n/a
        """
        pass

    def __getitem__(self, item) -> object:
        """Store an item in a data base.

        Args:
            item: The item to store.

        Returns:
            The object at the corresponding key
        """
        pass
