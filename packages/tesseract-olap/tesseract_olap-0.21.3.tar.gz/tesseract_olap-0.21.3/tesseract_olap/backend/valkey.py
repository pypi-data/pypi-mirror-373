import logging
from io import BytesIO
from typing import TYPE_CHECKING, Any, Union

import polars as pl
import redis as valkey
from pydantic import BaseModel, model_validator

from tesseract_olap.common import URL, hide_dsn_password
from tesseract_olap.exceptions.backend import UpstreamInternalError, UpstreamNotPrepared

from .cache import CacheConnection, CacheConnectionStatus, CacheProvider

if TYPE_CHECKING:
    from tesseract_olap.query import AnyQuery

logger = logging.getLogger(__name__)


class ValkeyConnectionParams(BaseModel):
    dsn: str
    default_ttl: int = 0

    @model_validator(mode="before")
    @classmethod
    def parse_dsn(cls, value):
        if isinstance(value, (str, URL)):
            value = URL(str(value))
            default_ttl, *_ = [*value.query_params.pop("default_ttl", []), "0"]
            return {"dsn": str(value), "default_ttl": default_ttl}

        return value


class ValkeyProvider(CacheProvider):
    connection_kwargs: dict[str, Any]
    dsn: str
    pool: valkey.ConnectionPool

    def __init__(self, dsn: Union[str, URL], **kwargs):
        params = ValkeyConnectionParams.model_validate(dsn)
        pool = valkey.ConnectionPool.from_url(params.dsn, **kwargs)

        self.connection_kwargs = {
            "default_ttl": params.default_ttl,
            "single_connection_client": True,
        }
        self.dsn = params.dsn
        self.pool = pool

    def __repr__(self):
        return f"{type(self).__name__}(dsn='{hide_dsn_password(self.dsn)}')"

    def connect(self):
        try:
            return ValkeyConnection(self.pool, **self.connection_kwargs)
        except valkey.ConnectionError as exc:
            message = "Attempt to use a not-open Redis connection."
            raise UpstreamNotPrepared(message, *exc.args) from exc
        except valkey.RedisError as exc:
            message = f"Redis{type(exc).__name__}:\n" + "\n".join(repr(arg) for arg in exc.args)
            raise UpstreamInternalError(message, *exc.args) from exc

    def clear(self):
        with valkey.Redis(connection_pool=self.pool) as conn:
            _ = conn.flushdb()


class ValkeyConnection(CacheConnection):
    client: valkey.Redis
    default_ttl: int

    def __init__(self, pool: valkey.ConnectionPool, default_ttl: int = -1, **kwargs):
        self.client = valkey.Redis(connection_pool=pool, **kwargs)
        self.default_ttl = default_ttl

    @property
    def status(self) -> CacheConnectionStatus:
        return (
            CacheConnectionStatus.CONNECTED
            if self.client.connection is not None and self.client.ping()
            else CacheConnectionStatus.CLOSED
        )

    def close(self) -> None:
        return self.client.close()

    def set(self, key: str, value: bytes) -> None:
        try:
            expires = self.default_ttl if self.default_ttl > 0 else None
            _ = self.client.set(key, value, ex=expires)
        except valkey.RedisError as exc:
            logger.exception("Error storing data under %r", key, exc_info=exc)

    def get(self, key: str) -> Union[bytes, None]:
        try:
            result = self.client.get(key)
        except valkey.ConnectionError as exc:
            logger.exception("Error retrieving data under %r", key, exc_info=exc)
        except valkey.RedisError as exc:
            logger.exception("Error retrieving data under %r", key, exc_info=exc)
        else:
            if result is None:
                return None
            if isinstance(result, bytes):
                return result
            logger.error("Unknown response under %r: %r", key, result)

    def exists(self, query: "AnyQuery") -> bool:
        return self.client.exists(query.key) == 1

    def store(self, query: "AnyQuery", data: "pl.DataFrame") -> None:
        dfio = data.write_ipc(file=None, compression="lz4")
        self.set(query.key, dfio.getvalue())

    def retrieve(self, query: "AnyQuery") -> Union["pl.DataFrame", None]:
        blob = self.get(query.key)
        return None if blob is None else pl.read_ipc(BytesIO(blob))

    def ping(self) -> bool:
        res = self.client.ping()
        return res in ("PONG", b"PONG")
