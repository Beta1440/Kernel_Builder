"""A database handler for shelve."""
import shelve

from cement.core.handler import CementBaseHandler
from kbuilder.cli.interface.database import IDatabase
from unipath.path import Path


class ShelveHandler(CementBaseHandler):
    class Meta:
        interface = IDatabase
        label = 'shelve_handler'
        description = 'This handler implements DatabaseInterface'
        config_defaults = dict(
            foo='bar'
            )

    my_var = 'This is my var'

    def __init__(self):
        super().__init__()
        self.app = None
        self.local_root = None

    def _setup(self, app):
        self.app = app
        self.local_root = app.active_kernel.root

    def store(self, item: object, key: str) -> None:
        """Store an item in a data base.

        Args:
            item: The item to store.

        Returns:
            The object at the corresponding key
        """
        with shelve.open(self._local_entry_path(key)) as db:
            db[key] = item

    def retrieve(self, key: str) -> object:
        """Retrieve an item from shelve.

        Args:
            key: The key item to retrieve.

        Returns:
            The object at the corresponding key.
        """
        with shelve.open(self._local_entry_path(key)) as db:
            item = db[key]
        return item

    def _local_entry_path(self, key: str) -> Path:
        return self.local_root.child('.kbuilder', '{}.db'.format(key))
