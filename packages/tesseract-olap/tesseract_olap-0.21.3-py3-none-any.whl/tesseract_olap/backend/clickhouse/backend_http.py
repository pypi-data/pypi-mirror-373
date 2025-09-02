from __future__ import annotations

import logging
import random
import threading
import uuid
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Literal, overload

import clickhouse_connect.dbapi.connection as chc
import polars as pl
from clickhouse_connect.driver.exceptions import DatabaseError, InterfaceError
from clickhouse_connect.driver.external import ExternalData
from httpx import URL

from tesseract_olap import __title__, __version__
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
    from tesseract_olap.schema import InlineTable, SchemaTraverser


logger = logging.getLogger(__name__)


class ClickhouseCursor(Cursor[chc.Cursor, T]):
    """Base class for the Cursor in this module with common methods."""

    def __init__(self, cursor: chc.Cursor):
        super().__init__(cursor)
        self._inline_tables: set[InlineTable] = set()

    @contextmanager
    def _exception_wrapper(self) -> Generator[None, Any, None]:
        try:
            yield
        except InterfaceError as exc:
            raise UpstreamNotPrepared(*exc.args) from exc
        except DatabaseError as exc:
            raise UpstreamInternalError(*exc.args) from exc

    def execute(self, operation: str, parameters: Mapping[str, str] | None = None) -> None:
        if not self.is_open:
            raise UpstreamNotPrepared

        data = ExternalData()
        for table in self._inline_tables:
            tsv = table.to_dataframe().write_csv(include_header=False, separator="\t")
            data.add_file(
                file_name=f"{table.name}.tsv",
                mime_type="text/tab-separated-values",
                structure=", ".join(
                    f"{name} {ClickhouseDataType.from_datatype(dtype)}"
                    for name, dtype in zip(table.headers, table.types)
                ),
                data=tsv.encode("utf-8"),
            )

        cursor = self._cursor

        query_result = cursor.client.query(
            operation,
            None if parameters is None else dict(parameters),
            external_data=data if data.files else None,
        )

        cursor.data = query_result.result_set
        cursor._rowcount = len(cursor.data)
        cursor._summary.append(query_result.summary)

        if query_result.column_names:
            cursor.names = query_result.column_names
            cursor.types = [x.name for x in query_result.column_types]
        elif cursor.data:
            cursor.names = [f"col_{x}" for x in range(len(cursor.data[0]))]
            cursor.types = [x.__class__ for x in cursor.data[0]]

    def set_inline_table(self, table: InlineTable) -> None:
        self._inline_tables.add(table)

    def reset_cursor(self) -> None:
        cursor_cls = type(self._cursor)
        self._cursor = cursor_cls(self._cursor.client)
        self._inline_tables.clear()


class TupleCursor(ClickhouseCursor[tuple[Any, ...]]):
    def fetchone(self) -> tuple[Any, ...] | None:
        with self._exception_wrapper():
            result = self._cursor.fetchone()
        return None if result is None else result

    def fetchmany(self, size: int = -1) -> list[tuple[Any, ...]]:
        with self._exception_wrapper():
            result = self._cursor.fetchmany(size)
        return [] if result is None else list(result)

    def fetchall(self) -> list[tuple[Any, ...]]:
        with self._exception_wrapper():
            result = self._cursor.fetchall()
        return [] if result is None else list(result)


class DictCursor(ClickhouseCursor[dict[str, Any]]):
    def fetchone(self) -> dict[str, Any] | None:
        with self._exception_wrapper():
            result = self._cursor.fetchone()
        return None if result is None else dict(zip(self._cursor.names, result))

    def fetchmany(self, size: int = -1) -> list[dict[str, Any]]:
        with self._exception_wrapper():
            result = self._cursor.fetchmany(size) or []
        return [dict(zip(self._cursor.names, row)) for row in result]

    def fetchall(self) -> list[dict[str, Any]]:
        with self._exception_wrapper():
            result = self._cursor.fetchall() or []
        return [dict(zip(self._cursor.names, row)) for row in result]


class ClickhouseHttpBackend(Backend):
    """Clickhouse HTTP Backend class.

    This is the main implementation for Clickhouse using HTTP protocol of the
    core :class:`Backend` class.

    Must be initialized with a connection string with the parameters for the
    Clickhouse database. Then must be connected before used to execute queries,
    and must be closed after finishing use.
    """

    dsn: str

    TupleCursor = TupleCursor
    DictCursor = DictCursor

    def __init__(self, dsn: str) -> None:
        """Create a new instance of the class."""
        self.dsn = dsn

    def startup_tasks(self, schema: SchemaTraverser, **kwargs: dict[str, bool]) -> None:
        """Run tasks intended for the startup process."""
        thread = threading.current_thread()
        thread_msg = "background" if thread.name == "startup_tasks" else "main thread"

        if kwargs.get("validate_schema"):
            msg = "Validating %r against ClickhouseHttpBackend in the %s"
            logger.debug(msg, schema, thread_msg)
            with self.new_session() as session, session.cursor("tuple") as cursor:
                validate_schema_tables(schema, cursor)

        if kwargs.get("count_members"):
            msg = "Updating full member count according to ClickhouseHttpBackend in the %s"
            logger.debug(msg, thread_msg)
            with self.new_session() as session, session.cursor("dict") as cursor:
                count_members(schema, cursor)

    def new_session(self, cache: CacheProvider | None = None, **kwargs) -> ClickhouseHttpSession:
        """Create a new Session object for a Clickhouse HTTP connection."""
        return ClickhouseHttpSession(self.dsn, cache=cache, **kwargs)

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


class ClickhouseHttpSession(Session):
    """Session class for Clickhouse HTTP connections."""

    _cache: CacheConnection
    _connection: chc.Connection

    cache: CacheProvider
    chunk_limit: int
    dsn: str
    query_limit: int
    session_id: str

    def __init__(
        self,
        dsn: str,
        *,
        cache: CacheProvider | None = None,
        chunk_limit: int = 100000,
        query_limit: int = 1000000,
    ) -> None:
        self.cache = DummyProvider() if cache is None else cache
        self.chunk_limit = chunk_limit
        self.dsn = dsn
        self.query_limit = query_limit
        self.session_id = f"{uuid.uuid4()}"

    def __repr__(self) -> str:
        dsn = URL(self.dsn)
        dsn = dsn.copy_with(username=dsn.username, password="***")  # noqa: S106
        return f"{type(self).__name__}(dsn='{dsn}')"

    def connect(self):
        self._cache = self.cache.connect()
        try:
            self._connection = chc.Connection(
                dsn=self.dsn,
                client_name=f"{__title__} {__version__}",
                session_id=self.session_id,
            )
        except DatabaseError as exc:
            self.close()
            raise UpstreamInternalError(*exc.args) from exc

    def close(self):
        if hasattr(self, "_cache"):
            self._cache.close()
            delattr(self, "_cache")
        if hasattr(self, "_connection"):
            self._connection.close()
            delattr(self, "_connection")

    @overload
    def cursor(self) -> TupleCursor: ...
    @overload
    def cursor(self, kind: Literal["tuple"]) -> TupleCursor: ...
    @overload
    def cursor(self, kind: Literal["dict"]) -> DictCursor: ...

    def cursor(self, kind: str = "tuple") -> ClickhouseCursor:
        """Create a new cursor of the provided type."""
        cursor = self._connection.cursor()
        if kind == "tuple":
            return TupleCursor(cursor)
        if kind == "dict":
            return DictCursor(cursor)
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
            page={"limit": pagi.limit, "offset": pagi.offset, "total": count or data.height},
        )
