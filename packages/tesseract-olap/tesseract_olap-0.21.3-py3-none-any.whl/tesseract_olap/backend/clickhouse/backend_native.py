from __future__ import annotations

import logging
import random
import threading
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Literal, overload

import clickhouse_driver as chdr
import clickhouse_driver.dbapi.connection as chdrconn
import polars as pl
from clickhouse_driver.dbapi import DatabaseError, InterfaceError
from clickhouse_driver.errors import Error as DriverError
from httpx import URL

from tesseract_olap.backend import (
    Backend,
    CacheConnection,
    CacheProvider,
    Cursor,
    DummyProvider,
    Result,
    Session,
    chunk_queries,
    growth_calculation,
    rename_columns,
    topk_calculation,
)
from tesseract_olap.common import AnyDict, AnyTuple, T
from tesseract_olap.exceptions.backend import (
    BackendLimitsException,
    UpstreamInternalError,
    UpstreamNotPrepared,
)
from tesseract_olap.query import AnyQuery, DataQuery

from .cursor import (
    count_members,
    fetch_count,
    fetch_dataframe,
    fetch_result,
    query_to_builder,
    validate_schema_tables,
)
from .debug import debug_single_query
from .dialect import ClickhouseDataType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from tesseract_olap.schema import InlineTable, SchemaTraverser

logger = logging.getLogger(__name__)


class ClickhouseCursor(Cursor[chdrconn.Cursor, T]):
    @contextmanager
    def _exception_wrapper(self):
        try:
            yield

        except DriverError as exc:
            raise UpstreamInternalError(exc.args[0]) from exc

        except InterfaceError as super_exc:
            args = super_exc.args or []
            exc = args[0]
            if isinstance(exc, DriverError):
                msg, *_ = str(exc.message).split("Stack trace:", 1)
                msg = f"Clickhouse{type(exc).__name__}({exc.code}): {msg}"
                super_exc = exc
            else:
                msg = f"Clickhouse{type(exc).__name__}" + (f": {args[0]}" if args else "")
            raise UpstreamNotPrepared(msg, *args) from super_exc

        except DatabaseError as super_exc:
            args = super_exc.args or []
            exc = args[0]
            if isinstance(exc, DriverError):
                msg, *_ = str(exc.message).split("Stack trace:", 1)
                msg = f"Clickhouse{type(exc).__name__}({exc.code}): {msg}"
                super_exc = exc
            else:
                msg = f"Clickhouse{type(exc).__name__}" + (f": {args[0]}" if args else "")
            raise UpstreamInternalError(msg, *args) from super_exc

    def reset_cursor(self) -> None:
        self._cursor._reset_state()
        self._cursor.set_query_id(self.query_id)

    def set_inline_table(self, table: InlineTable) -> None:
        tblmeta_gen = (ClickhouseDataType[item.name].value for item in table.types)
        structure = zip(table.headers, tblmeta_gen)
        self._cursor.set_external_table(table.name, list(structure), table.rows)

    def set_query_id(self, value: str) -> None:
        self.query_id = value
        self._cursor.set_query_id(value)


class TupleCursor(ClickhouseCursor[tuple[Any, ...]]):
    """A Cursor class to fetch data in tuples."""

    def fetchone(self) -> tuple[Any, ...] | None:
        with self._exception_wrapper():
            result = self._cursor.fetchone()
        assert result is None or isinstance(result, tuple)
        return result

    def fetchmany(self, size: int = -1) -> list[tuple[Any, ...]]:
        with self._exception_wrapper():
            result = self._cursor.fetchmany(size)
        assert result is None or isinstance(result, list)
        return [] if result is None else result

    def fetchall(self) -> list[tuple[Any, ...]]:
        with self._exception_wrapper():
            result = self._cursor.fetchall()
        assert result is None or isinstance(result, list)
        return [] if result is None else result


class DictCursor(ClickhouseCursor[dict[str, Any]]):
    """A Cursor class to fetch data as a dicts."""

    def fetchone(self) -> dict[str, Any] | None:
        with self._exception_wrapper():
            result = self._cursor.fetchone()
        return None if result is None else dict(zip(self.columns, result))

    def fetchmany(self, size: int = -1):
        with self._exception_wrapper():
            result = self._cursor.fetchmany(size) or []
        assert isinstance(result, list)
        return [dict(zip(self.columns, row)) for row in result]

    def fetchall(self):
        with self._exception_wrapper():
            result = self._cursor.fetchall() or []
        assert isinstance(result, list)
        return [dict(zip(self.columns, row)) for row in result]

    @property
    def columns(self) -> Iterable[str]:
        """Yield the column names in the returned data."""
        columns = self._cursor.columns_with_types or []
        return (name for name, _ in columns)


class ClickhouseBackend(Backend):
    """Clickhouse Native Backend class.

    This is the main implementation for Clickhouse of the core :class:`Backend`
    class.

    Must be initialized with a connection string with the parameters for the
    Clickhouse database. Then must be connected before used to execute queries,
    and must be closed after finishing use.
    """

    dsn: str

    TupleCursor = TupleCursor
    DictCursor = DictCursor

    def __init__(self, dsn: str) -> None:
        """Create a new instance.

        Arguments:
          dsn: The Data Source Name for the connection with the Clickhouse server.

        """
        self.dsn = dsn

    def startup_tasks(self, schema: SchemaTraverser, **kwargs) -> None:
        """Run tasks intended for the startup process."""
        thread = threading.current_thread()
        thread_msg = "background" if thread.name == "startup_tasks" else "main thread"

        if kwargs.get("validate_schema"):
            msg = "Validating %r against ClickhouseBackend in the %s"
            logger.debug(msg, schema, thread_msg)
            with self.new_session() as session, session.cursor() as cursor:
                validate_schema_tables(schema, cursor)

        if kwargs.get("count_members"):
            msg = "Updating full member count according to ClickhouseBackend in the %s"
            logger.debug(msg, thread_msg)
            with self.new_session() as session, session.cursor("dict") as cursor:
                count_members(schema, cursor)

    def new_session(self, cache: CacheProvider | None = None, **kwargs) -> ClickhouseSession:
        """Create a new Session object for a Clickhouse connection."""
        return ClickhouseSession(self.dsn, cache=cache, **kwargs)

    def ping(self) -> bool:
        """Check if the current connection is working correctly."""
        with self.new_session() as session, session.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        return result == (1,)

    def debug_query(self, query: AnyQuery, **kwargs) -> AnyDict:
        """Return the generated queries/metadata used in the process of fetching data."""
        count_qb, count_meta = query_to_builder(query, count=True)
        data_qb, data_meta = query_to_builder(query)
        return {
            "count": debug_single_query(count_qb.get_sql(), count_meta),
            "data": debug_single_query(data_qb.get_sql(), data_meta),
        }


class ClickhouseSession(Session):
    """Session class for Clickhouse connections."""

    _cache: CacheConnection
    _connection: chdrconn.Connection

    cache: CacheProvider
    chunk_limit: int
    dsn: str
    query_limit: int

    def __init__(
        self,
        dsn: str,
        *,
        cache: CacheProvider | None = None,
        chunk_limit: int = 100_000,
        query_limit: int = 1_000_000,
    ) -> None:
        """Create a new instance.

        Arguments:
          dsn: The Data Source Name for the connection with the Clickhouse server.

        Keyword Arguments:
          cache: An instance of CacheProvider, to use when retrieving DataFrames.
            (Default: a :class:`DummyProvider` instance)
          chunk_limit: The max number of rows to fetch per request against the server.
            (Default: 100_000)
          query_limit: The max number of rows to fetch in a single fetch call.
            (Default: 1_000_000)

        """
        self.cache = DummyProvider() if cache is None else cache
        self.dsn = dsn
        self.chunk_limit = chunk_limit
        self.query_limit = query_limit

    def __repr__(self) -> str:
        dsn = URL(self.dsn)
        dsn = dsn.copy_with(username=dsn.username, password="***")  # noqa: S106
        return f"{type(self).__name__}(dsn='{dsn}')"

    def connect(self):
        self._cache = self.cache.connect()
        try:
            self._connection = chdr.connect(dsn=self.dsn, compression="lz4")
            with self.cursor() as cursor:
                cursor.execute("SELECT 1")
                assert cursor.fetchone() == (1,)
        except (AssertionError, ValueError, DatabaseError) as exc:
            self.close()
            raise UpstreamInternalError(*exc.args) from exc

    def close(self):
        try:
            self._cache.close()
            delattr(self, "_cache")
        except AttributeError:
            pass
        try:
            self._connection.close()
            delattr(self, "_connection")
        except AttributeError:
            pass

    @overload
    def cursor(self) -> TupleCursor: ...
    @overload
    def cursor(self, kind: Literal["tuple"]) -> TupleCursor: ...
    @overload
    def cursor(self, kind: Literal["dict"]) -> DictCursor: ...

    def cursor(self, kind: Literal["tuple", "dict"] = "tuple") -> ClickhouseCursor:
        cursor = self._connection.cursor()
        if kind == "dict":
            return DictCursor(cursor)
        if kind == "tuple":
            return TupleCursor(cursor)
        msg = f"Invalid cursor result format: '{kind}'"
        raise ValueError(msg)

    def fetch(self, query: AnyQuery, **kwargs) -> Result[list[AnyTuple]]:
        """Execute the query and return the data as a list of tuples."""
        with self.cursor() as cursor:
            return fetch_result(query, cursor)

    def fetch_records(self, query: AnyQuery, **kwargs) -> Result[list[AnyDict]]:
        """Execute the query and return the data as a list of dictionaries."""
        with self.cursor("dict") as cursor:
            return fetch_result(query, cursor)

    def fetch_dataframe(self, query: AnyQuery, **kwargs) -> Result[pl.DataFrame]:
        """Execute the query and returns the data as a polars DataFrame."""
        cursor = self.cursor()
        cursor.set_query_id(f"{query.key}_{random.randrange(4294967296):08x}")  # noqa: S311

        df_list: list[pl.DataFrame] = []
        pagi = query.pagination

        count = fetch_count(query, cursor, cache=self._cache)
        if 0 < self.query_limit < count and (pagi.limit == 0 or pagi.limit > self.query_limit):
            total = count if pagi.limit == 0 else pagi.limit
            msg = (
                f"This request intends to retrieve {total} rows of data, "
                "which is too large for the OLAP server to handle. "
                "Please reformulate the request with more limitations and try again."
            )
            raise BackendLimitsException(msg)

        logger.debug(
            "Query %s is %d rows; %r",
            query.key,
            count,
            pagi,
            extra={"query": repr(query)},
        )

        cache_status = "HIT"
        for chunk_query in chunk_queries(query, limit=self.chunk_limit):
            cursor.reset_cursor()
            cache_status, chunk_data = fetch_dataframe(chunk_query, cursor, cache=self._cache)

            logger.debug(
                "%s for chunk %r: %s (%.3fmb)",
                type(self.cache).__name__,
                chunk_query.key,
                cache_status,
                chunk_data.estimated_size("mb"),
                extra={"query": repr(chunk_query)},
            )

            if chunk_data.height > 0 or not df_list:
                df_list.append(chunk_data)
                if chunk_data.height < self.chunk_limit:
                    break
            else:
                break

        cursor.close()

        data = pl.concat(df_list) if len(df_list) > 1 else df_list[0]
        if isinstance(query, DataQuery):
            # Do growth calculation if query.growth exists
            data = growth_calculation(query, data)
            # Do TopK calculation if query.topk and query.growth exists
            data = topk_calculation(query, data)
            # Rename the columns according to the aliases
            data = rename_columns(query, data)

        return Result(
            data=data.slice(pagi.offset % self.chunk_limit, pagi.limit or None),
            columns=query.columns,
            cache={"key": query.key, "status": cache_status},
            page={
                "limit": pagi.limit,
                "offset": pagi.offset,
                "total": count or data.height,
            },
        )
