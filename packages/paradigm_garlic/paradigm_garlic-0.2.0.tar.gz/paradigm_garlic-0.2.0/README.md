
# garlic 🧄

cli and python interface for interacting with Snowflake

Features
- run queries against snowflake using simple UX
- auto-convert query results to polars dataframes
- convenience functions for:
    - formatting timestamps for use in SQL queries
    - setting the warehouse
    - listing databases, schemas, tables, and query history


## Installation

```bash
uv add paradigm_garlic
```

## Usage Example

#### Simplest example
```python
import garlic

dataframe = garlic.query('SELECT * FROM my_table')
```

#### Query using custom credentials
```python
import garlic

dataframe = garlic.query('SELECT * FROM my_table')
```

#### Set different default warehouse:
```python
import garlic

garlic.set_warehouse('BIG_WAREHOUSE')
dataframe = garlic.query('SELECT * FROM my_table')
```

#### Read from Snowflake management tables

```python
import garlic

databases = garlic.list_databases()
schemas = garlic.list_schemas()
tables = garlic.list_tables()
query_history = garlic.list_query_history()
```

### Use timestamps in CLI queries

```python
import garlic
import datetime

sql = """
SELECT *
FROM my_table
WHERE
    block_timestamp >= {start_time}
    AND block_timestamp < {end_time}
""".format(
    start_time=garlic.format_timestamp('2024-01-01', utc=True),
    end_time=garlic.format_timestamp(datetime.datetime.now(), utc=True),
)

dataframe = garlic.query(sql)
```
