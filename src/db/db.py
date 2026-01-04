import duckdb as db

DEFAULT_TABLE_LIST = ["users", "rota_names", "change_dates", "rota_snapshots", "overrides"]

def build_db(
    table_list: list[str], 
    root_fp: str
) -> db.DuckDBPyConnection:
    database = db.connect(database=":memory:")

    for table in table_list:
        file_path = f"{root_fp}/{table}.csv"
        database.sql(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{file_path}')")

    return database