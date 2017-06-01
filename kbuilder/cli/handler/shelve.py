"""A database handler for shelve."""
import shelve

from cement.core.handler import CementBaseHandler
from unipath.path import Path

from kbuilder.cli.interface.database import Database


class ShelveHandler(CementBaseHandler):
    class Meta:
        interface = Database
        label = 'shelve_handler'
        description = 'Store and retrieve objects'
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

    def __setitem__(self, key: str, value: object) -> object:
        """Store an item in a data base.

        Args:
            key: the key to use to retrieve the item
            item: The item to store.

            Returns: n/a
        """
        with shelve.open(self._local_entry_path(key)) as db:
            db[key] = value

    def __getitem__(self, key) -> object:
        """Store an item in a data base.

        Args:
            key: The key to use in getting the item.

            Returns:
                The object at the corresponding key
        """
        with shelve.open(self._local_entry_path(key)) as db:
            return db[key]

    def _local_entry_path(self, key: str) -> Path:
        return self.local_root.child('.kbuilder', '{}.db'.format(key))
