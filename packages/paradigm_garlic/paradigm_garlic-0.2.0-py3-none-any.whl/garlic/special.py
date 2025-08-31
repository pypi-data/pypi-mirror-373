from __future__ import annotations

import typing

from . import env
from . import execute

if typing.TYPE_CHECKING:
    import polars as pl
    from snowflake.connector import SnowflakeConnection
    from snowflake.connector.cursor import SnowflakeCursor


def list_databases(
    *,
    cursor: SnowflakeCursor | None = None,
    conn: SnowflakeConnection | None = None,
) -> pl.DataFrame:
    import polars as pl

    if cursor is None:
        cursor = env.get_cursor(conn=conn)

    cursor.execute('SHOW DATABASES')
    raw = cursor.fetchall()

    raw_schema: dict[str, pl.DataType | type[pl.DataType]] = {
        'created_on': pl.Datetime(
            time_unit='us', time_zone='America/Los_Angeles'
        ),
        'name': pl.String,
        'is_default': pl.String,
        'is_current': pl.String,
        'origin': pl.String,
        'owner': pl.String,
        'comment': pl.String,
        'options': pl.String,
        'retention_time': pl.String,
        'kind': pl.String,
        'owner_role_type': pl.String,
        'object_visibility': pl.String,
    }

    catalogs = pl.DataFrame(
        raw,
        schema=raw_schema,
        orient='row',
        infer_schema_length=999999,
    )

    return catalogs


def list_schemas(
    catalog: str | list[str] | None = None,
    cursor: 'SnowflakeCursor' | None = None,
    conn: 'SnowflakeConnection' | None = None,
) -> 'pl.DataFrame':
    import polars as pl

    if isinstance(catalog, str):
        sql = 'SELECT * FROM {catalog}.INFORMATION_SCHEMA.SCHEMATA'.format(
            catalog=catalog
        )
        return (
            execute.query(sql, cursor=cursor, conn=conn)
            .filter(pl.col('SCHEMA_NAME') != 'INFORMATION_SCHEMA')
            .sort('CATALOG_NAME', 'SCHEMA_NAME')
        )

    elif isinstance(catalog, list) or catalog is None:
        if catalog is None:
            catalogs = list_databases(cursor=cursor, conn=conn)
            catalog = catalogs['name'].to_list()

        results: list[pl.DataFrame] = []
        for item in catalog:
            if item in ('SNOWFLAKE_SAMPLE_DATA',):
                continue
            try:
                df = list_schemas(item, cursor=cursor, conn=conn)
                results.append(df)
            except Exception:
                print('could not access', item)
        if not results:
            raise Exception('no accessible catalogs found')
        return pl.concat(results, how='vertical_relaxed')

    else:
        raise ValueError('catalog must be str, list[str], or None')


def list_tables(
    catalog: str | list[str],
    all_columns: bool = False,
    cursor: SnowflakeCursor | None = None,
    conn: SnowflakeConnection | None = None,
) -> pl.DataFrame:
    import polars as pl

    # get list of catalogs
    if catalog is None:
        catalogs = list_databases(cursor=cursor, conn=conn)
        catalog = catalogs['name'].to_list()

    # get tables of each catalog
    if isinstance(catalog, list):
        results = []
        for item in catalog:
            if item == 'SNOWFLAKE_SAMPLE_DATA':
                continue
            print('getting tables of', item)
            try:
                df = list_tables(
                    item, cursor=cursor, conn=conn, all_columns=all_columns
                )
                results.append(df)
            except Exception:
                print('could not access', item)
        return pl.concat(results)

    # execute query
    sql = 'SELECT * FROM {catalog}.INFORMATION_SCHEMA.TABLES'.format(
        catalog=catalog
    )
    df = execute.query(sql, cursor=cursor, conn=conn)

    # process result
    df = df.filter(pl.col.TABLE_SCHEMA != 'INFORMATION_SCHEMA')
    if not all_columns:
        columns = [
            'TABLE_CATALOG',
            'TABLE_SCHEMA',
            'TABLE_NAME',
            'TABLE_TYPE',
            'IS_TRANSIENT',
            'ROW_COUNT',
            'BYTES',
            'CLUSTERING_KEY',
            'LAST_ALTERED',
        ]
        df = df.select(columns)
    df = df.sort('TABLE_CATALOG', 'TABLE_SCHEMA', 'TABLE_NAME')

    return df


def list_query_history(
    *,
    n: int | None = None,
    all_columns: bool = False,
    cursor: SnowflakeCursor | None = None,
    conn: SnowflakeConnection | None = None,
) -> pl.DataFrame:
    if all_columns:
        columns = '*'
    else:
        column_names = [
            'QUERY_TEXT',
            'USER_NAME',
            'START_TIME',
            'END_TIME',
            'EXECUTION_STATUS',
            'BYTES_SCANNED',
            'BYTES_READ_FROM_RESULT',
            'BYTES_WRITTEN',
            'BYTES_WRITTEN_TO_RESULT',
            'BYTES_DELETED',
            'ROWS_PRODUCED',
            'ROWS_WRITTEN_TO_RESULT',
            'ROWS_INSERTED',
            'ROWS_UPDATED',
            'ROWS_DELETED',
            'ROWS_UNLOADED',
            'PERCENTAGE_SCANNED_FROM_CACHE',
            'QUERY_HASH',
        ]
        columns = ','.join(column_names)
    sql = 'SELECT {columns} FROM snowflake.account_usage.query_history'.format(
        columns=columns
    )
    sql = sql + ' ORDER BY START_TIME DESC'

    if n is not None:
        sql = sql + ' LIMIT ' + str(n)

    return execute.query(sql, conn=conn, cursor=cursor).sort('START_TIME')
