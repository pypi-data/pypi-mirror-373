from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Literal

import polars as pl
from pypika.terms import Function, Term, ValueWrapper

from tesseract_olap.backend import CacheConnection, Cursor, ParamManager, Result
from tesseract_olap.backend.cache import DummyConnection
from tesseract_olap.common import AnyTuple, T
from tesseract_olap.exceptions.backend import BackendValidationError
from tesseract_olap.query import AnyQuery, DataQuery, MembersQuery
from tesseract_olap.schema import CubeTraverser, InlineTable, Measure, SchemaTraverser

from .dialect import ClickhouseDataType, ClickHouseQuery
from .sql_data import sql_dataquery
from .sql_members import sql_cubemembers, sql_membersquery

logger = logging.getLogger(__name__)


def fetch(query: AnyQuery, cursor: Cursor[Any, T], *, count: bool = False) -> list[T]:
    """Execute the query and return the data as defined by the cursor type."""
    qbuilder, meta = query_to_builder(query, count=count)

    for table in meta.tables:
        cursor.set_inline_table(table)
    cursor.execute(qbuilder.get_sql(), parameters=meta.params)
    return cursor.fetchall()


def fetch_count(
    query: AnyQuery,
    cursor: Cursor[Any, AnyTuple],
    *,
    cache: CacheConnection | None = None,
) -> int:
    """Get the count of rows the provided query will return."""
    cache = DummyConnection() if cache is None else cache
    data = cache.get(query.count_key)

    if data is None:
        data = fetch(query, cursor, count=True)
        count = data[0][0] if data and isinstance(data[0], tuple) else 0
        cache.set(query.count_key, count.to_bytes(4, "big"))
    else:
        count = int.from_bytes(data, "big")

    return count


def fetch_dataframe(
    query: AnyQuery,
    cursor: Cursor[Any, AnyTuple],
    *,
    cache: CacheConnection | None = None,
    count: bool = False,
) -> tuple[Literal["HIT", "MISS"], pl.DataFrame]:
    """Execute the query, optionally through cache, and return the data as a polars DataFrame."""
    cache_status = "HIT"
    cache = DummyConnection() if cache is None else cache
    data = cache.retrieve(query)

    if data is None:
        qbuilder, meta = query_to_builder(query, count=count)

        for table in meta.tables:
            cursor.set_inline_table(table)

        schema = None
        if isinstance(query, DataQuery):
            schema = {
                msrfi.name: pl.Float64 for msrfi in query.fields_quantitative if msrfi.is_measure
            }

        data = pl.read_database(
            query=qbuilder.get_sql(),
            connection=cursor,
            execute_options={"parameters": meta.params},
            schema_overrides=schema,
        )

        cache.store(query, data)
        cache_status = "MISS"

    return cache_status, data


def fetch_result(query: AnyQuery, cursor: Cursor[Any, T]) -> Result[list[T]]:
    """Execute the query, get the data as defined by the Cursor, and wrap it in a Result."""
    data = fetch(query, cursor)
    limit, offset = query.pagination.as_tuple()
    return Result(
        data=list(data),
        columns=query.columns,
        cache={"key": query.key, "status": "MISS"},
        page={"limit": limit, "offset": offset, "total": len(data)},
    )


def query_to_builder(query: AnyQuery, *, count: bool = False) -> tuple[Term, ParamManager]:
    """Translate any kind of query into an SQL builder object and its extra parameters."""
    if isinstance(query, DataQuery):
        return sql_dataquery(query, count=count)

    if isinstance(query, MembersQuery):
        return sql_membersquery(query, count=count)

    raise ValueError("unreachable")  # noqa: EM101


def extract_member_count(
    cube: CubeTraverser,
    cursor: Cursor[Any, dict[str, int]],
) -> dict[str, int]:
    query, meta = sql_cubemembers(cube)

    cursor.reset_cursor()
    for table in meta.tables:
        cursor.set_inline_table(table)
    cursor.execute(query.get_sql())

    return cursor.fetchone() or {"_empty": 0}


def count_members(schema: SchemaTraverser, cursor: Cursor[Any, dict[str, int]]) -> None:
    """Query the backend for an updated number of members of each Level."""
    count_total = sum(
        len(hie.level_map)
        for cube in schema.cube_map.values()
        for dim in cube.dimensions
        for hie in dim.hierarchies
    )
    count_progress = 0

    for cube in sorted(schema.cube_map.values(), key=lambda cube: cube.name):
        members = extract_member_count(cube, cursor)
        count_progress += len(members)

        for level in cube.levels:
            level.count = members.get(level.name, 0)
            if level.count == 0:
                logger.warning(
                    "Level(cube=%r, name=%r) returned 0 members",
                    cube.name,
                    level.name,
                )

        args = (cube.name, count_progress, count_total)
        logger.debug("Updated member count for cube %r (%d/%d)", *args, extra=members)


def validate_schema_tables(schema: SchemaTraverser, cursor: Cursor) -> None:
    """Validate the tables and columns declared in the Schema entities against the Backend."""
    schema_tables = unwrap_tables(schema)
    logger.debug("Tables to validate: %d", len(schema_tables))

    sql = (
        "SELECT table, groupArray(name) AS columns "
        "FROM system.columns "
        "WHERE table IN splitByChar(',', %(tables)s) "
        "GROUP BY table"
    )
    cursor.execute(sql, {"tables": ",".join(schema_tables.keys())})
    observed_tables = {table: set(columns) for table, columns in (cursor.fetchall() or [])}

    if schema_tables != observed_tables:
        reasons = []

        for table, columns in schema_tables.items():
            if table not in observed_tables:
                reasons.append(
                    f"- Table '{table}' is defined in Schema but not available in Backend",
                )
                continue

            difference = columns.difference(observed_tables[table])
            if difference:
                reasons.append(
                    f"- Schema references columns {difference} in table '{table}', but not available in Backend",
                )

        if reasons:
            message = (
                "Mismatch between columns defined in the Schema and available in ClickhouseBackend:\n"
                + "\n".join(reasons)
            )
            raise BackendValidationError(message)


def unwrap_tables(self: SchemaTraverser) -> dict[str, set[str]]:
    """Extract the {table: column[]} data from all entities in the schema."""
    tables: dict[str, set[str]] = defaultdict(set)

    for cube in self.cube_map.values():
        table = cube.table
        if isinstance(table, InlineTable):
            continue

        # Index fact tables
        tables[table.name].update(
            (
                item.key_column
                for measure in cube.measures
                for item in measure.and_submeasures()
                if isinstance(item, Measure)
            ),
            (dimension.foreign_key for dimension in cube.dimensions),
        )

        for hierarchy in cube.hierarchies:
            table = hierarchy.table
            if table is None or isinstance(table, InlineTable):
                continue

            # Index dimension tables
            tables[table.name].update(
                (
                    item
                    for level in hierarchy.levels
                    for item in (level.key_column, *level.name_column_map.values())
                ),
                (
                    item
                    for propty in hierarchy.properties
                    for item in propty.key_column_map.values()
                ),
            )

    return dict(tables)


def table_to_sql(table: InlineTable):
    headers = ", ".join(
        f"{name} {ClickhouseDataType.from_datatype(dtype)}"
        for name, dtype in zip(table.headers, table.types)
    )
    fn = Function("VALUES", ValueWrapper(headers), *table.rows)
    return ClickHouseQuery.from_(fn).select("*")
