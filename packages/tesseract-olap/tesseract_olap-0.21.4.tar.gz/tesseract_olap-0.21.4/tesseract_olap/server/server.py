from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import overload
from urllib.parse import parse_qs

from typing_extensions import deprecated

from tesseract_olap.backend import (
    Backend,
    CacheProvider,
    DummyProvider,
    LfuProvider,
    Result,
    Session,
)
from tesseract_olap.common import AnyTuple
from tesseract_olap.exceptions import BackendError
from tesseract_olap.exceptions.query import InvalidQuery
from tesseract_olap.exceptions.server import UnknownBackendError
from tesseract_olap.query import (
    AnyQuery,
    AnyRequest,
    DataQuery,
    DataRequest,
    MembersQuery,
    MembersRequest,
)
from tesseract_olap.schema import Schema, SchemaTraverser

from .schema import setup_schema

logger = logging.getLogger(__name__)


class OlapServer:
    """Main server class.

    This object manages the connection with the backend database and the schema
    instance containing the database references, to enable make queries against
    them.
    """

    schema: SchemaTraverser
    backend: Backend
    cache: CacheProvider

    def __init__(
        self,
        *,
        backend: str | Backend,
        schema: str | Path | Schema,
        cache: str | CacheProvider = "",
    ) -> None:
        self.backend = backend if isinstance(backend, Backend) else _setup_backend(backend)

        self.cache = cache if isinstance(cache, CacheProvider) else _setup_cache(cache)

        self.schema = SchemaTraverser(
            schema if isinstance(schema, Schema) else setup_schema(schema),
        )

    @property
    def raw_schema(self) -> Schema:
        """Retrieve the raw Schema instance used by this server."""
        return self.schema.schema

    def startup_tasks(self, **kwargs) -> None:
        """Define some tasks expected to be run at the startup."""

        def background_task():
            if kwargs.get("validate_schema"):
                self.schema.validate()
            try:
                self.backend.startup_tasks(self.schema, **kwargs)
            except BackendError as exc:
                logger.exception(exc.message, exc_info=exc)

        thread = threading.Thread(name="startup_tasks", target=background_task, daemon=True)
        thread.start()

    @overload
    def build_query(self, request: DataRequest) -> DataQuery: ...

    @overload
    def build_query(self, request: MembersRequest) -> MembersQuery: ...

    def build_query(self, request: AnyRequest) -> AnyQuery:
        """Use the Schema to validate a Request and generate its matching Query instance."""
        if isinstance(request, DataRequest):
            return DataQuery.from_request(self.schema, request)
        if isinstance(request, MembersRequest):
            return MembersQuery.from_request(self.schema, request)

        msg = "Attempt to build a Query using an invalid Request instance."
        raise InvalidQuery(msg)

    def clear_cache(self) -> None:
        """Clear all stored items in the cache."""
        self.cache.clear()

    def debug_query(self, query: AnyQuery) -> dict[str, str]:
        """Build the SQL query for a Query instance, according to the configured backend."""
        return self.backend.debug_query(query)

    @deprecated("The session() method allows to reuse a connection for multiple queries.")
    def execute(self, request: AnyRequest) -> Result[list[AnyTuple]]:
        """Quick method to get a result from a Request object.

        It's deprecated and will be removed at some point.
        """
        query = self.build_query(request)
        with self.session() as session:
            return session.fetch(query)

    def ping(self) -> bool:
        """Perform a ping call to the backend server.

        A succesful call should make this function return :bool:`True`.
        """
        try:
            return self.backend.ping()
        except Exception:  # noqa: BLE001
            return False

    def session(self, **kwargs) -> Session:
        """Generate a new Session object with the provisioned Backend."""
        return self.backend.new_session(cache=self.cache, **kwargs)


def _setup_backend(dsn: str) -> Backend:
    """Generate a new instance of a backend, guessing from the provided connection string.

    If it can't find a compatible backend, raises :class:`UnknownBackendError`.
    """
    if dsn.startswith(("clickhouse+http:", "clickhouse+https:")):
        from tesseract_olap.backend.clickhouse import ClickhouseHttpBackend

        return ClickhouseHttpBackend(dsn.removeprefix("clickhouse+"))

    if dsn.startswith(("clickhouse:", "clickhouses:")):
        from tesseract_olap.backend.clickhouse import ClickhouseBackend

        return ClickhouseBackend(dsn)

    raise UnknownBackendError(dsn)


def _setup_cache(dsn: str) -> CacheProvider:
    """Generate a new instance of a CacheProvider bundled in this package."""
    if dsn.startswith(":memory:"):
        try:
            params = parse_qs(dsn.removeprefix(":memory:"), strict_parsing=True)
            maxsize = params.get("maxsize", ["64"])
            dfsize = params.get("dfsize", ["150"])
            return LfuProvider(maxsize=int(maxsize[0]), dfsize=int(dfsize[0]))
        except ValueError:
            return LfuProvider()

    if dsn.startswith("sqlite:"):
        from tesseract_olap.backend.sqlite import SQLiteCacheProvider

        return SQLiteCacheProvider(dsn.removeprefix("sqlite:"))

    if dsn.startswith(("valkey:", "valkeys:", "redis:", "rediss:")):
        from tesseract_olap.backend.valkey import ValkeyProvider

        return ValkeyProvider(dsn)

    return DummyProvider()
