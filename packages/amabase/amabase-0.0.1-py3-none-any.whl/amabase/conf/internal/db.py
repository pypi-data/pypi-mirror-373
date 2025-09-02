from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from functools import cached_property
from pathlib import Path
from sqlite3 import Connection, OperationalError, connect
from typing import Any

from amabase.utils import datetime_from_utc_timestamp, decode_json, decode_sequence, encode_json, encode_sequence, tabulate

_logger = logging.getLogger(__name__)

class Db:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Db()
        return cls._instance

    def __init__(self):
        if self.__class__._instance is not None:
            raise ValueError(f"Already instanciated: {self.__class__}")
        self.__class__._instance = self
        
        self.configured = False
        self._connection: Connection|None = None
    
    @property
    def path(self) -> Path:
        if not self.configured:
            raise AttributeError("ManageDb not configured yet")
        if self._path == '__django__':
            from django.conf import settings
            return Path(settings.DATABASES['default']['NAME'])
        return self._path # type: ignore
    
    def configure(self, *, path: str|os.PathLike, reconfigure = False):
        if self.configured and not reconfigure:
            raise AttributeError("ManageDb already configured")
        self._path = path
        self.configured = True

    @property
    def connection(self) -> Connection:
        if self._connection is None:
            if self._path == '__django__':
                _logger.debug("Use django connection to %s", self.path)

                from django.db import connections
                self._connection = connections['default'] # pyright: ignore[reportAttributeAccessIssue]

            else:
                _logger.debug("Connect to %s", self.path)
                self.path.parent.mkdir(parents=True, exist_ok=True)

                # NOTE: we use autocommit because Django uses autocommit by default...
                # This should avoid mistakes
                if sys.version_info < (3, 12):
                    self._connection = connect(self.path, isolation_level=None)
                else:
                    self._connection = connect(self.path, autocommit=True)
            
            self.migrate()
        
        return self._connection # pyright: ignore[reportReturnType]
    
    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    #region Properties

    @property
    def size(self) -> int:
        self.connection # ensure created
        return self.path.stat().st_size

    @property
    def last_modified_at(self) -> datetime:
        self.connection # ensure created
        return datetime.fromtimestamp(self.path.stat().st_mtime).astimezone().replace(microsecond=0)

    def get_prop(self, key: str) -> Any:
        cursor = self.connection.execute("SELECT value FROM _prop WHERE key = ?", [key])
        row = cursor.fetchone()
        return row[0] if row is not None else None

    def get_or_set_prop(self, key: str, default: Any) -> Any:
        value = self.get_prop(key)
        if value is not None:
            return value
        self.set_prop(key, default)
        return default
    
    def get_list_prop(self, key: str) -> list|None:
        value = self.get_prop(key)
        if value is None or value == '':
            return None
        return decode_sequence(value)
    
    def get_json_prop(self, key: str) -> Any:
        value = self.get_prop(key)
        return decode_json(value)

    def set_prop(self, key: str, value: Any):
        if isinstance(value, (list, set, tuple)):
            value = encode_sequence(value)
        elif isinstance(value, dict):
            value = encode_json(value)
        elif isinstance(value, Path):
            value = str(value)

        self.connection.execute("INSERT INTO _prop (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value", [key, value])

    @cached_property
    def initialized_at(self) -> datetime:
        return datetime_from_utc_timestamp(self.get_prop('initialized.at'))

    @cached_property
    def initialized_sqlite_version(self) -> str:
        return self.get_prop('initialized.sqlite_version')

    @cached_property
    def sqlite_version(self) -> str:
        cursor = self.connection.execute('SELECT sqlite_version()')
        return cursor.fetchone()[0]

    @cached_property
    def spatialite_version(self) -> str|None:
        try:
            cursor = self.connection.execute('SELECT spatialite_version()')
            return cursor.fetchone()[0]        
        except OperationalError as err:
            if str(err) == "no such function: spatialite_version":
                return None
            else:
                raise

    #endregion


    #region Migrations
    
    def migrate(self):
        prv_last_migration_name = self._get_last_migration_name()
        new_last_migration_name = None
        migrations_dir = Path(__file__).parent.parent.joinpath('migrations')
        for migration in sorted(filter(lambda path: not path.name.startswith('~'), migrations_dir.glob('*.sql'))):
            if prv_last_migration_name is None or migration.stem > prv_last_migration_name:
                self._apply_migration(migration)
                new_last_migration_name = migration.stem

        if new_last_migration_name is not None:
            self.connection.execute("INSERT INTO _prop (key, value) VALUES ('last_migration.name', ?), ('last_migration.at', unixepoch()) ON CONFLICT (key) DO UPDATE SET value = excluded.value", [new_last_migration_name])

    def _get_last_migration_name(self) -> str|None:
        try:
            cursor = self.connection.execute("SELECT value FROM _prop WHERE key = 'last_migration.name'")
        except OperationalError as err:
            if str(err) == "no such table: _prop":
                return None
            else:
                raise

        row = cursor.fetchone()
        return row[0] if row is not None else None
    
    def _apply_migration(self, path: Path):
        _logger.debug("Apply migration %s", path.stem)
        self.connection.executescript(path.read_text(encoding='utf-8'))

    @cached_property
    def last_migration_name(self) -> str|None:
        return self.get_prop('last_migration.name')
    
    @cached_property
    def last_migration_at(self) -> datetime|None:
        return datetime_from_utc_timestamp(self.get_prop('last_migration.at'))
    
    #endregion
