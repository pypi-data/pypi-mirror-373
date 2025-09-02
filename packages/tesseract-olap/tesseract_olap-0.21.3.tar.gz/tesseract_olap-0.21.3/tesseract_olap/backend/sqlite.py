from __future__ import annotations

import sqlite3
import threading
import time

import polars as pl

from tesseract_olap.query import AnyQuery

from .cache import CacheConnection, CacheConnectionStatus, CacheProvider


class SQLiteCacheProvider(CacheProvider):
    """Implements a CacheProvider using a SQLite database as backend."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value BLOB,
                    expires_at INTEGER
                )
                """,
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON kv_store (expires_at);")

    def connect(self) -> SQLiteCacheConnection:
        return SQLiteCacheConnection(self.db_path)

    def clear(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM kv_store;")


class SQLiteCacheConnection(CacheConnection):
    """Implements a CacheConnection using a SQLite database as Backend."""

    def __init__(self, db_path: str, *, default_ttl: int = -1):
        self.db_path = db_path
        self.default_ttl = default_ttl
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.lock = threading.Lock()
        self._status = CacheConnectionStatus.CONNECTED

    @property
    def status(self) -> CacheConnectionStatus:
        return self._status

    def close(self) -> None:
        self.conn.close()
        self._status = CacheConnectionStatus.CLOSED

    def set(self, key: str, value: bytes) -> None:
        expires_at = int(time.time()) + self.default_ttl if self.default_ttl > -1 else None
        with self.lock, self.conn:
            self.conn.execute(
                """
                INSERT INTO kv_store (key, value, expires_at) VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    expires_at=excluded.expires_at;
                """,
                (key, value, expires_at),
            )

    def get(self, key: str) -> bytes | None:
        now = int(time.time())
        with self.lock, self.conn:
            self.conn.execute(
                "DELETE FROM kv_store WHERE expires_at IS NOT NULL AND expires_at <= ?;",
                (now,),
            )
            row = self.conn.execute(
                """
                SELECT value FROM kv_store
                WHERE key = ? AND (expires_at IS NULL OR expires_at > ?);
                """,
                (key, now),
            ).fetchone()
        return None if row is None else row[0]

    def store(self, query: AnyQuery, data: pl.DataFrame) -> None:
        dfio = data.write_ipc(file=None, compression="lz4")
        self.set(query.key, dfio.getvalue())

    def retrieve(self, query: AnyQuery) -> pl.DataFrame | None:
        blob = self.get(query.key)
        return None if blob is None else pl.read_ipc(blob)

    def ping(self) -> bool:
        try:
            self.conn.execute("SELECT 1;")
        except sqlite3.Error:
            return False
        else:
            return True
