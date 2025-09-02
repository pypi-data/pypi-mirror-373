import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from queue import Empty, Queue
from typing import Any, Iterator, Protocol

import pyodbc

from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)


class DatabaseConnection(Protocol):
    """Protocol for database connections."""

    def execute(self, sql: str, params: Any = None) -> Any:
        """Execute SQL query."""
        ...

    def commit(self) -> None:
        """Commit transaction."""
        ...

    def close(self) -> None:
        """Close connection."""
        ...

    def cursor(self) -> Any:
        """Get cursor for executing queries."""
        ...


class ConnectionFactory(ABC):
    """Abstract factory for creating database connections."""

    @abstractmethod
    def create_connection(self) -> DatabaseConnection:
        """Create a new database connection."""
        pass

    @abstractmethod
    def is_connection_healthy(self, conn: DatabaseConnection) -> bool:
        """Check if connection is healthy."""
        pass


class SQLiteConnectionFactory(ConnectionFactory):
    """Factory for creating SQLite connections."""

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with proper configuration."""
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30.0,
            isolation_level=None,  # autocommit mode
        )
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        return conn

    def is_connection_healthy(self, conn: DatabaseConnection) -> bool:
        """Check if a SQLite connection is healthy."""
        try:
            conn.execute("SELECT 1").fetchone()
            return True
        except Exception:
            return False


class AzureSQLConnectionFactory(ConnectionFactory):
    """Factory for creating Azure SQL connections."""

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string

    def create_connection(self) -> pyodbc.Connection:
        """Create a new Azure SQL connection."""
        conn = pyodbc.connect(self.connection_string)
        conn.autocommit = True
        return conn

    def is_connection_healthy(self, conn: pyodbc.Connection) -> bool:
        """Check if an Azure SQL connection is healthy."""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False


class ConnectionPool:
    """Database-agnostic connection pool with health checks and retry logic."""

    def __init__(
        self,
        connection_factory: ConnectionFactory,
        pool_size: int = 8,
        max_retries: int = 3,
        retry_delay: float = 0.1,
    ) -> None:
        self.connection_factory = connection_factory
        self.pool_size = pool_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._pool: Queue[Any] = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0

        # Pre-populate the pool
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize the connection pool with healthy connections."""
        for _ in range(self.pool_size):
            try:
                conn = self.connection_factory.create_connection()
                if self.connection_factory.is_connection_healthy(conn):
                    self._pool.put(conn)
                    self._created_connections += 1
                else:
                    conn.close()
            except Exception:
                # If we can't create initial connections, we'll create them on demand
                break

    @contextmanager
    def get_connection(self) -> Iterator[DatabaseConnection]:
        """Context manager to get a connection from the pool."""
        conn = None
        retry_count = 0

        while retry_count <= self.max_retries:
            try:
                # Try to get a connection from the pool
                try:
                    conn = self._pool.get(timeout=5.0)
                except Empty:
                    # Pool is empty, create a new connection
                    with self._lock:
                        if (
                            self._created_connections < self.pool_size * 2
                        ):  # Allow some overflow
                            conn = self.connection_factory.create_connection()
                            self._created_connections += 1
                        else:
                            # Wait a bit and try again
                            time.sleep(self.retry_delay)
                            retry_count += 1
                            continue

                # Check if connection is healthy
                if conn and self.connection_factory.is_connection_healthy(conn):
                    try:
                        yield conn
                        # Return connection to pool if still healthy
                        if self.connection_factory.is_connection_healthy(conn):
                            self._pool.put_nowait(conn)
                        else:
                            conn.close()
                            with self._lock:
                                self._created_connections -= 1
                        return
                    except Exception as e:
                        # If there was an error using the connection, close it
                        if conn:
                            try:
                                conn.close()
                            except Exception:
                                pass
                            with self._lock:
                                self._created_connections -= 1
                        raise e
                else:
                    # Connection is unhealthy, close it and retry
                    if conn:
                        try:
                            conn.close()
                        except Exception:
                            pass
                        with self._lock:
                            self._created_connections -= 1

                    retry_count += 1
                    if retry_count <= self.max_retries:
                        time.sleep(
                            self.retry_delay * retry_count
                        )  # Exponential backoff

            except Exception as e:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass
                    with self._lock:
                        self._created_connections -= 1

                retry_count += 1
                if retry_count <= self.max_retries:
                    time.sleep(self.retry_delay * retry_count)
                else:
                    raise RuntimeError(
                        f"Failed to get database connection after {self.max_retries} retries: {e}"
                    )

        raise RuntimeError(
            f"Failed to get database connection after {self.max_retries} retries"
        )

    def close_all(self) -> None:
        """Close all connections in the pool."""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except (Empty, Exception):
                break

        with self._lock:
            self._created_connections = 0
