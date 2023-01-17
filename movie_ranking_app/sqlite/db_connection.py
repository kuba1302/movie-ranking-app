import sqlite3
from contextlib import contextmanager
from pathlib import Path


def _sqlite_con(db_file: str = "db.db"):
    return sqlite3.connect(Path(__file__).parents[2] / db_file)


def dict_from_row(row):
    return dict(zip(row.keys(), row))


@contextmanager
def get_database_connection():
    con = _sqlite_con()
    yield con
    con.close()


@contextmanager
def get_database_cursor():
    con = _sqlite_con()
    # Return dict instead of tuple
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    yield cur
    con.close()


@contextmanager
def get_database_cursor_and_commit():
    con = _sqlite_con()
    cur = con.cursor()
    yield cur
    con.commit()
    con.close()
