import duckdb as db
from pathlib import Path
import pandas as pd
from src.db.db import DEFAULT_TABLE_LIST, DB
from test.helpers import get_random_consistent_row, parse_datetime_columns

def test_build_db(shared_db: DB) -> None:
    tables = {item[0] for item in shared_db.get_db().sql("SHOW TABLES").fetchall()}

    assert tables == set(DEFAULT_TABLE_LIST)

def test_fresh_db(fresh_db: DB) -> None:
    tables = {item[0] for item in fresh_db.get_db().sql("SHOW TABLES").fetchall()}

    assert tables == set(DEFAULT_TABLE_LIST)

def test_write_tables_to_csv_single_table(fresh_db: DB, tmp_path: Path) -> None:
    updated_table = _update_table_with_new_consistent_row(fresh_db, DEFAULT_TABLE_LIST[0])

    fresh_db.write_tables_to_csv(DEFAULT_TABLE_LIST[0:1])
    written_table = parse_datetime_columns(pd.read_csv(f"{tmp_path}/{DEFAULT_TABLE_LIST[0]}.csv"))

    assert updated_table.equals(written_table)

def test_write_tables_to_csv_all_tables(fresh_db: DB, tmp_path: Path) -> None:
    updated_tables: dict[str, pd.DataFrame] = {}
    for table_name in DEFAULT_TABLE_LIST:
        updated_tables[table_name] = _update_table_with_new_consistent_row(fresh_db, table_name)

    fresh_db.write_tables_to_csv()
    for table_name in DEFAULT_TABLE_LIST:
        written_table = parse_datetime_columns(pd.read_csv(f"{tmp_path}/{table_name}.csv"))
        assert updated_tables[table_name].equals(written_table)

def _update_table_with_new_consistent_row(fresh_db: DB, table_name: str) -> pd.DataFrame:
    current_table = fresh_db.get_db().sql(f"SELECT * FROM {table_name}").df()
    if current_table.empty:
        _cast_all_columns_to_strings(current_table)
    
    new_row = get_random_consistent_row(current_table)
    fresh_db.get_db().sql(f"""
        INSERT INTO {table_name}
        VALUES ({', '.join([f"'{str(new_row[v])}'" for v in current_table.columns])})
    """)
    
    updated_table = pd.concat([current_table, pd.DataFrame([new_row])], ignore_index=True)
    return updated_table

def _cast_all_columns_to_strings(df: pd.DataFrame) -> None:
    for col in df.columns:
        df[col] = df[col].astype(str)
