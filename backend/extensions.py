"""Database connection pool and shared extensions."""
import os
from mysql.connector import pooling
from contextlib import contextmanager
from config import Config

_pool = None


def init_db_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="jewelry_pool",
            pool_size=int(os.getenv("DB_POOL_SIZE", "3")),
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            autocommit=False,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
        )
    return _pool


@contextmanager
def get_db():
    """Yield a connection from the pool, ensuring it gets returned."""
    if _pool is None:
        init_db_pool()
    conn = _pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor(dictionary=True, commit=False):
    """Yield a cursor with auto-commit/rollback semantics."""
    with get_db() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
