import duckdb as db

def load_db(
    table_list: list[str], 
    root_fp: str
) -> None:
    for table in table_list:
        db.register(table, db.read_csv(f"{root_fp}/{table}.csv"))