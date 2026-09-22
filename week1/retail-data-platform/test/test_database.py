import sqlite3
import unittest
from pathlib import Path

from retail_ingestion.database import connect_database, open_database


class TestDatabase(unittest.TestCase):
    def test_connect_database_returns_connection(self) -> None:
        connection = connect_database(Path(":memory:"))

        try:
            self.assertIsInstance(connection, sqlite3.Connection)
        finally:
            connection.close()

    def test_open_database_closes_connection_after_with_block(self) -> None:
        with open_database(Path(":memory:")) as connection:
            result = connection.execute("SELECT 1").fetchone()
            self.assertEqual(result, (1,))

        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute("SELECT 1")