import duckdb as db

def build_db(
    table_list: list[str], 
    root_fp: str
) -> db.DuckDBPyConnection:
    database = db.connect(database=":memory:")

    for table in table_list:
        file_path = f"{root_fp}/{table}.csv"
        database.sql(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{file_path}')")

    return database