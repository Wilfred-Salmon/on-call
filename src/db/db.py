import duckdb as db

DEFAULT_TABLE_LIST = ["users", "rota_names", "change_dates", "rota_snapshots", "overrides"]

class DB:
    _table_list: list[str]
    _root_fp: str
    _db: db.DuckDBPyConnection

    def __init__(self, table_list: list[str], root_fp: str) -> None:
        self._table_list = table_list
        self._root_fp = root_fp

        self._build()

    def _build(self) -> None:
        self._db = db.connect(database=":memory:")

        for table in self._table_list:
            file_path = f"{self._root_fp}/{table}.csv"
            self._db.sql(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{file_path}')")
    
    def get_db(self) -> db.DuckDBPyConnection:
        return self._db
    
    def close(self) -> None:
        self._db.close()
    
    def __enter__(self) -> db.DuckDBPyConnection:
        return self._db
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._db.close()
