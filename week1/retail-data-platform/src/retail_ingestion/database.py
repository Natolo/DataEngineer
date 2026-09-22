import sqlite3
from pathlib import Path
from collections.abc import Iterator
from contextlib import contextmanager

def connect_database(database_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(database_path)

@contextmanager
def open_database(database_path: Path) -> Iterator[sqlite3.Connection]:
    connection = connect_database(database_path)
    try:
        yield connection
    finally:
        connection.close()