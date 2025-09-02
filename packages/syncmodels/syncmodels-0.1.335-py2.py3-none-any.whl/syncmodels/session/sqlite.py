import re
import sqlite3
from ..crud import parse_duri

from ..definitions import (
    URI,
)


from .sql import iSQLSession


class SQLiteSession(iSQLSession):
    "Based on sqlite, change methods as needed"

    DEFAULT_METHOD = "get"

    async def hide_inspect_schema(self, uri, kind):
        """
        info
        ({'date': {'name': 'date',
                   'type': 'TEXT',
                   'notnull': 0,
                   'default': None,
                   'pk': 0,
                   'hidden': 0},
          'value': {'name': 'value',
                    'type': 'REAL',
                    'notnull': 0,
                    'default': None,
                    'pk': 0,
                    'hidden': 0}},
         [{'name': 'date',
           'type': 'TEXT',
           'notnull': 0,
           'default': None,
           'pk': 0,
           'hidden': 0},
          {'name': 'value',
           'type': 'REAL',
           'notnull': 0,
           'default': None,
           'pk': 0,
           'hidden': 0}],
         'date')
        """
        connection = sqlite3.connect(uri["path"])
        cursor = connection.cursor()

        columns = "name", "type", "notnull", "default", "pk", "hidden"
        fields = [
            {columns[i]: value for i, value in enumerate(row[1:])}
            for row in cursor.execute(f"PRAGMA table_xinfo({kind});")
        ]
        d_fields = {_["name"]: _ for _ in fields}

        # try to precalculate the MONOTONIC_SINCE_KEY
        # TODO: move to base class
        def best():
            for value in d_fields:
                for pattern in self.MONOTONIC_CANDIDATES:
                    if re.match(pattern, value):
                        return value

        monotonic_since_key = best()
        info = d_fields, fields, monotonic_since_key
        return info

    async def _create_connection(self, uri: URI, **_uri):
        _uri = parse_duri(uri)
        connection = sqlite3.connect(_uri["path"])
        cursor = connection.cursor()
        return cursor


SQLiteSession.register_itself(r"sqlite://")
