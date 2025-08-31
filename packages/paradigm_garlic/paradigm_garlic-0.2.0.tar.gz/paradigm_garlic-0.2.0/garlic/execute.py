from __future__ import annotations

import typing
from . import env

if typing.TYPE_CHECKING:
    import polars as pl
    from snowflake.connector import SnowflakeConnection
    from snowflake.connector.cursor import SnowflakeCursor


def query(
    sql: str,
    *,
    cursor: SnowflakeCursor | None = None,
    conn: SnowflakeConnection | None = None,
) -> pl.DataFrame:
    import polars as pl
    import snowflake.connector

    if cursor is None:
        cursor = env.get_cursor(conn=conn)
    cursor.execute(sql)

    try:
        arrow_table = cursor.fetch_arrow_all()  # type: ignore
        return pl.from_arrow(arrow_table)  # type: ignore
    except snowflake.connector.errors.NotSupportedError as e:
        if cursor._query_result_format == 'json':
            all_results = cursor.fetchall()
            if all_results == [('Statement executed successfully.',)]:
                return pl.DataFrame(all_results)
        raise e
