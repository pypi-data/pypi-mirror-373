"""Backend model definitions module.

This module contains abstract definitions for the interfaces of the Backend
class. Tesseract is compatible with any kind of data source as long as there's a
backend class that adapts the Query and the Results to the defined interface.
"""

from __future__ import annotations

import abc
import uuid
from copy import copy
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
)

from tesseract_olap.common import T, shorthash
from tesseract_olap.exceptions.backend import UpstreamNotPrepared
from tesseract_olap.query import AnyQuery, DataQuery, PaginationIntent
from tesseract_olap.schema import DataType, InlineTable

if TYPE_CHECKING:
    from collections.abc import Generator, Mapping, Sequence
    from types import TracebackType

    import polars as pl

    from tesseract_olap.common import AnyDict, AnyTuple
    from tesseract_olap.schema import SchemaTraverser


class ExternalCursor(Protocol):
    @property
    def description(self) -> list[tuple[str, str, None, None, None, None, bool]] | None: ...

    def close(self) -> None: ...

    def execute(self, operation: str, parameters: Mapping[str, str] = {}): ...

    def fetchone(self) -> Any: ...

    def fetchmany(self, size: int = -1) -> Sequence | None: ...

    def fetchall(self) -> Sequence | None: ...


C = TypeVar("C", bound=ExternalCursor)


class Cursor(Generic[C, T]):
    def __init__(self, cursor: C):
        self._cursor = cursor
        self.query_id = uuid.uuid4().hex
        self.is_open = True

    def __enter__(self: Cursor[C, T]) -> Cursor[C, T]:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self.is_open = False
        self._cursor.close()

    @property
    def description(self) -> list[tuple[str, str, None, None, None, None, bool]] | None:
        return self._cursor.description

    def execute(self, operation: str, parameters: Mapping[str, str] = {}) -> None:
        if not self.is_open:
            raise UpstreamNotPrepared
        self._cursor.execute(operation, parameters)

    def fetchone(self) -> T | None:
        raise NotImplementedError

    def fetchmany(self) -> list[T]:
        raise NotImplementedError

    def fetchall(self) -> list[T]:
        raise NotImplementedError

    def reset_cursor(self) -> None:
        raise NotImplementedError

    def set_inline_table(self, table: InlineTable) -> None:
        raise NotImplementedError

    def set_query_id(self, value: str) -> None:
        self.query_id = value


class CacheMeta(TypedDict):
    key: str
    status: str


class PaginationMeta(TypedDict):
    total: int
    limit: int
    offset: int


@dataclass(eq=False, order=False)
class Result(Generic[T]):
    """Wrapper for the result of the executed queries.

    It also contains the metadata related to the query execution.
    """

    data: T
    columns: dict[str, DataType]
    cache: CacheMeta = field(
        default_factory=lambda: {"key": "0" * 32, "status": "MISS"},
    )
    page: PaginationMeta = field(
        default_factory=lambda: {"limit": 0, "offset": 0, "total": 0},
    )


class Backend(abc.ABC):
    """Base class for database backends compatible with Tesseract."""

    @abc.abstractmethod
    def startup_tasks(self, schema: SchemaTraverser, **kwargs) -> None:
        """Run tasks intended for the startup process.

        The user should mind multiple instances of the OlapServer could be called in
        parallel against the same remote backend, so idempotence should be a principle
        in the execution of this function.
        """

    @abc.abstractmethod
    def new_session(self, **kwargs) -> Session:
        """Establish the connection to the backend server.

        This operation must be done before running any other data method, and
        must be separate from the creation of a :class:`Backend` instance.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def ping(self) -> bool:
        """Perform a ping call to the backend server.

        If the call is successful, this function should return :bool:`True`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def debug_query(self, query: AnyQuery, **kwargs) -> dict[str, str]:
        """Return the generated queries/metadata used in the process of fetching data."""
        raise NotImplementedError


class Session(abc.ABC):
    """Base class for connections made to a backend compatible with Tesseract."""

    def __enter__(self):
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        self.close()

    @abc.abstractmethod
    def connect(self) -> None:
        """Establish the connection to the backend server.

        This operation is called automatically when the Session instance is
        used within a context manager.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """Close the connection to the backend server.

        This operation is called automatically at the end of the context manager
        this instance was called into.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def cursor(self, kind: Literal["tuple", "dict"] = "tuple") -> Cursor:
        """Return a Cursor proxy for the underlying backend driver."""
        raise NotImplementedError

    @abc.abstractmethod
    def fetch(self, query: AnyQuery, **kwargs) -> Result[list[AnyTuple]]:
        """Execute the query and returns the data as a list of tuples."""
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_dataframe(self, query: AnyQuery, **kwargs) -> Result[pl.DataFrame]:
        """Execute the query and returns the data as a polars DataFrame."""
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_records(self, query: AnyQuery, **kwargs) -> Result[list[AnyDict]]:
        """Execute the query and returns the data as a list of dictionaries."""
        raise NotImplementedError


@dataclass
class ParamManager:
    """Utility class to handle parameter names and external tables in a query.

    Keeps track of the SQL named parameters and their values, to combine them
    through all the functions where they're defined, and output them at the
    final generation step.
    """

    params: dict[str, str] = field(default_factory=dict)
    tables: list[InlineTable] = field(default_factory=list)

    def __init__(self, query: Optional[AnyQuery] = None) -> None:
        self.params = {}
        self.tables = []

        if isinstance(query, DataQuery):
            if isinstance(query.cube.table, InlineTable):
                self.tables.append(query.cube.table)
            self.tables.extend(
                hiefi.table
                for hiefi in query.fields_qualitative
                if isinstance(hiefi.table, InlineTable)
            )

    def set_param(self, value: str, key: Optional[str] = None) -> str:
        """Store a new named parameter value, and returns the parameter name."""
        key = f"p_{shorthash(value)}" if key is None else key
        self.params[key] = value
        return key

    def set_table(self, table: InlineTable) -> None:
        """Store an inline table."""
        self.tables.append(table)


def chunk_queries(query: AnyQuery, *, limit: int = 500000) -> Generator[AnyQuery, Any, None]:
    """Split a query intended to retrieve a large/uncertain amount of rows into smaller chunks."""
    if limit == 0:
        yield query
        return

    pagi = query.pagination
    index = pagi.offset // limit
    while True:
        chunk_query = copy(query)
        chunk_query.pagination = PaginationIntent(limit=limit, offset=index * limit)
        yield chunk_query

        index += 1
        if pagi.limit > 0 and index * limit > pagi.limit:
            break
