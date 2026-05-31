import duckdb as db

from enum import Enum


class SQL_TYPES(Enum):
    STRING = "STRING"
    INTEGER = "INTEGER"
    DATE = "DATE"


type DBSchema = dict[str, dict[str, SQL_TYPES]]

DEFAULT_TABLE_SCHEMA = {
    "users": {
        "user_id": SQL_TYPES.INTEGER,
        "name": SQL_TYPES.STRING,
    },
    "rota_names": {"rota_id": SQL_TYPES.INTEGER, "name": SQL_TYPES.STRING},
    "change_dates": {
        "rota_id": SQL_TYPES.INTEGER,
        "date": SQL_TYPES.DATE,
        "snapshot_id": SQL_TYPES.INTEGER,
    },
    "rota_snapshots": {
        "snapshot_id": SQL_TYPES.INTEGER,
        "user_id": SQL_TYPES.INTEGER,
        "index": SQL_TYPES.INTEGER,
    },
    "overrides": {
        "user_id": SQL_TYPES.INTEGER,
        "rota_id": SQL_TYPES.INTEGER,
        "start_date": SQL_TYPES.DATE,
        "duration": SQL_TYPES.INTEGER,
    },
}


class DB:
    _schema: DBSchema
    _table_list: list[str]
    _root_fp: str
    _delimiter: str
    _db: db.DuckDBPyConnection

    def __init__(
        self,
        schema: DBSchema,
        root_fp: str,
        delimiter: str = ",",
    ) -> None:
        self._schema = schema
        self._table_list = list(schema.keys())
        self._root_fp = root_fp
        self._delimiter = delimiter

        self._build()

    def _build(self) -> None:
        self._db = db.connect(database=":memory:")

        for table_name, columns in self._schema.items():
            file_path = f"{self._root_fp}/{table_name}.csv"
            column_schema = ",\n".join(
                f"'{name}': '{sql_type.value}'" for name, sql_type in columns.items()
            )
            self._db.sql(f"""
                CREATE TABLE {table_name} AS SELECT * FROM read_csv(
                    '{file_path}', 
                    delim='{self._delimiter}',
                    columns = {{ {column_schema} }}
                )
            """)

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
