import duckdb as db
from src.db import build_db, DEFAULT_TABLE_LIST

def test_build_db(shared_db: db.DuckDBPyConnection):
    tables = {item[0] for item in shared_db.sql("SHOW TABLES").fetchall()}

    assert tables == set(DEFAULT_TABLE_LIST)