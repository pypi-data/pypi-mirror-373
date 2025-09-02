from __future__ import annotations

import sys
from argparse import ArgumentParser

from amabase.utils import tabulate


class DbCommand:
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('sql', nargs='?', help="a raw SQL statement to execute in the database (if not provided, information about the database is displayed on the standard output)")


    def handle(self, sql: str|None = None, **options):
        """
        Run a raw SQL statement on the SQLite database.

        If not SQL statement is provided, information about the database is displayed on the standard output.
        """
        from amabase.conf import db

        if not sql:
            print(f"Path:               {db.path}")
            print(f"Size:               {db.size:,} bytes")
            print(f"Last modified:      {db.last_modified_at}")
            print(f"SQLite version:     {db.sqlite_version}")
            print("")
            print(f"Initialized:        {db.initialized_at}")
            print(f"(SQLite version):   {db.initialized_sqlite_version}")
            print("")
            print(f"Last migration:     {db.last_migration_at}")
            print(f"(name):             {db.last_migration_name}")
        else:
            cursor = db.connection.execute(sql)
            if cursor.description is None:
                print(f"Affected rows: {cursor.rowcount}")
            else:
                columns = [c[0] for c in cursor.description]
                rows = cursor.fetchall()
                sys.stdout.write(tabulate(rows, columns))
                sys.stdout.write('\n')
