"""User-facing entry point for mosaic."""

from typing import Dict, Optional, Any
from .core.sqlite_driver import SQLiteDriver
from .exceptions import UnsupportedDriverError


class Mosaic:
    """
    Main entrypoint for users.

    Usage:
        db = Mosaic("sqlite:///test.db")
        db.create_table("users", {"id": "int", "name": "str", "age": "int"})
        db.insert("users", {"name": "Akash", "age": 19})
        db.find("users")
        db.update("users", {"id": 1}, {"age": 20})
        db.delete("users", {"id": 1})
        db.close()
    """

    def __init__(self, db_url: str = "sqlite:///mosaic.db"):
        self.db_url = db_url
        self.driver = self._choose_driver(db_url)

    def _choose_driver(self, url: str):
        url = url.strip()
        if url.startswith("sqlite://"):
            return SQLiteDriver(url)
        elif url.startswith("mysql://"):
            from .core.mysql_driver import MySQLDriver
            return MySQLDriver(url)
        elif url.startswith("postgres://"):
            from .core.postgres_driver import PostgresDriver
            return PostgresDriver(url)
        elif url.startswith("mongodb://"):
            from .core.mongo_driver import MongoDriver
            return MongoDriver(url)
        raise UnsupportedDriverError(f"No driver for URL: {url}")

    # passthrough methods (thin layer)
    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        return self.driver.create_table(table_name, schema)

    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        return self.driver.insert(table_name, data)

    def find(self, table_name: str, filters: Optional[Dict[str, Any]] = None):
        return self.driver.find(table_name, filters)

    def update(self, table_name: str, filters: Dict[str, Any], new_values: Dict[str, Any]) -> int:
        return self.driver.update(table_name, filters, new_values)

    def delete(self, table_name: str, filters: Dict[str, Any]) -> int:
        return self.driver.delete(table_name, filters)

    def close(self):
        return self.driver.close()
