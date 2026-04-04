from types import TracebackType

import duckdb as db
from contextlib import AbstractContextManager

DEFAULT_TABLE_LIST = [
    "users",
    "rota_names",
    "change_dates",
    "rota_snapshots",
    "overrides",
]


class DB(AbstractContextManager[db.DuckDBPyConnection]):
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
            self._db.sql(
                f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{file_path}')"
            )

    def get_db(self) -> db.DuckDBPyConnection:
        return self._db

    def write_tables_to_csv(self, table_names: list[str] | None = None) -> None:
        if table_names is None:
            table_names = self._table_list

        for table_name in table_names:
            self._write_table_to_csv(table_name)

    def _write_table_to_csv(self, table_name: str) -> None:
        if table_name not in self._table_list:
            raise ValueError(f"table_name must be one of {self._table_list}")

        file_path = f"{self._root_fp}/{table_name}.csv"
        self._db.sql(f"COPY {table_name} TO '{file_path}' (FORMAT CSV, HEADER)")

    def close(self) -> None:
        self._db.close()

    def __enter__(self) -> db.DuckDBPyConnection:
        return self._db

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._db.close()
