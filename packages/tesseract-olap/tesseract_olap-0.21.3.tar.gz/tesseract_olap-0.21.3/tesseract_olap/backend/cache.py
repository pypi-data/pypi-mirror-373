from __future__ import annotations

import abc
from enum import Enum

import polars as pl
from lfudacache import LFUDACache

from tesseract_olap.query import AnyQuery

CacheConnectionStatus = Enum("CacheConnectionStatus", ["CLOSED", "CONNECTED"])


class CacheProvider(abc.ABC):
    """Base class for the implementation of a cache layer for the Backend."""

    def __repr__(self):
        return f"{type(self).__name__}"

    @abc.abstractmethod
    def connect(self) -> CacheConnection:
        """Create a new Connection with the cache backend."""
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self) -> None:
        """Clear all the stored keys in the cache backend."""
        raise NotImplementedError


class CacheConnection(abc.ABC):
    """Internal Base class for individual connections to the cache layer."""

    @property
    @abc.abstractmethod
    def status(self) -> CacheConnectionStatus:
        """Return the current state of the Connection against the cache backend."""
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """Close the connection against the backend, and update the status on this instance."""
        raise NotImplementedError

    @abc.abstractmethod
    def set(self, key: str, value: bytes) -> None:
        """Store raw data to the cache."""
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, key: str) -> bytes | None:
        """Retrieve raw data from the cache."""
        raise NotImplementedError

    @abc.abstractmethod
    def store(self, query: AnyQuery, data: pl.DataFrame) -> None:
        """Store an object in the cache backend."""
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve(self, query: AnyQuery) -> pl.DataFrame | None:
        """Retrieve an object from the cache backend. If not found, returns None."""
        raise NotImplementedError

    @abc.abstractmethod
    def ping(self) -> bool:
        """Check the connection against the cache backend is alive."""
        raise NotImplementedError


class DummyProvider(CacheProvider):
    """A CacheProvider used when the user doesn't set a valid one. Will always MISS."""

    def connect(self) -> DummyConnection:
        return DummyConnection()

    def clear(self) -> None:
        pass


class DummyConnection(CacheConnection):
    """The CacheConnection associated to DummyProvider. Will always MISS."""

    @property
    def status(self) -> CacheConnectionStatus:
        return CacheConnectionStatus.CONNECTED

    def close(self) -> None:
        pass

    def set(self, key: str, value: bytes) -> None:
        pass

    def get(self, key: str) -> bytes | None:
        return None

    def store(self, query: AnyQuery, data: pl.DataFrame) -> None:
        pass

    def retrieve(self, query: AnyQuery) -> pl.DataFrame | None:
        return None

    def ping(self):
        return True


class LfuProvider(CacheProvider):
    """Stores elements in a dictionary under the Least Frequently Used caching strategy."""

    def __init__(self, *, maxsize: int = 64, dfsize: int = 150) -> None:
        self.store = LFUDACache(maxsize)
        self.dfsize = dfsize

    def connect(self):
        return LfuConnection(self.store, self.dfsize)

    def clear(self):
        self.store.clear()  # type: ignore


class LfuConnection(CacheConnection):
    """The CacheConnection associated to LfuProvider."""

    def __init__(self, store: LFUDACache, dfsize: int = 150) -> None:
        self.storage = store
        self.dfsize = dfsize

    @property
    def status(self):
        return CacheConnectionStatus.CONNECTED

    def close(self) -> None:
        pass

    def set(self, key: str, value: bytes) -> None:
        self.storage[key] = value

    def get(self, key: str) -> bytes | None:
        return self.storage.get(key)

    def store(self, query: AnyQuery, data: pl.DataFrame) -> None:
        if data.estimated_size("mb") < self.dfsize:
            self.storage[query.key] = data

    def retrieve(self, query: AnyQuery) -> pl.DataFrame | None:
        return self.storage.get(query.key)

    def ping(self) -> bool:
        return True
