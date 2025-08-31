from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from snowflake.connector import SnowflakeConnection
    from snowflake.connector.cursor import SnowflakeCursor


_connection_cache: dict[str, SnowflakeConnection] = {}


def get_credentials() -> dict[str, str | None]:
    import os
    import json

    raw_credentials = os.environ.get('SNOWFLAKE_CREDENTIALS')
    if raw_credentials is None or raw_credentials == '':
        raise Exception(
            'set credentials as a JSON blob in SNOWFLAKE_CREDENTIALS environment variable'
        )
    credentials: dict[str, str | None] = json.loads(raw_credentials)
    return credentials


def get_connection(
    *,
    reset: bool = False,
    credentials: dict[str, str | None] | None = None,
) -> SnowflakeConnection:
    import json
    import snowflake.connector

    # get serialized credentials
    if credentials is None:
        credentials = get_credentials()
    serialized_credentials = json.dumps(credentials, sort_keys=True)

    if serialized_credentials in _connection_cache and not reset:
        # load from cache if possible
        return _connection_cache[serialized_credentials]
    else:
        # create new connection and cache it
        conn = snowflake.connector.connect(**credentials)
        _connection_cache[serialized_credentials] = conn
        return conn


def get_cursor(
    *,
    conn: SnowflakeConnection | None = None,
    credentials: dict[str, str | None] | None = None,
) -> SnowflakeCursor:
    if conn is None:
        conn = get_connection(credentials=credentials)
    return conn.cursor()


def set_warehouse(
    warehouse: str,
    *,
    conn: SnowflakeConnection | None = None,
    credentials: dict[str, str | None] | None = None,
) -> None:
    cursor = get_cursor(conn=conn, credentials=credentials)
    cursor.execute('USE WAREHOUSE ' + warehouse)
