# src/my_db_library/core/__init__.py
from .config import settings
from .database import connection, init_db
from .exc import DBConnectException, NotFoundError

__all__ = ["settings", "connection", "init_db"]
