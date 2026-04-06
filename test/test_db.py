from pathlib import Path
import pandas as pd
import pytest
from typing import Callable
from src.db.db import DEFAULT_TABLE_SCHEMA, DB
from test.helpers import get_random_consistent_row, parse_datetime_columns


def test_build_db(shared_db: DB) -> None:
    tables = {item[0] for item in shared_db.get_db().sql("SHOW TABLES").fetchall()}

    assert tables == set(DEFAULT_TABLE_SCHEMA.keys())


def test_fresh_db(fresh_db: DB) -> None:
    tables = {item[0] for item in fresh_db.get_db().sql("SHOW TABLES").fetchall()}

    assert tables == set(DEFAULT_TABLE_SCHEMA.keys())


def test_write_tables_to_csv_single_table(fresh_db: DB, tmp_path: Path) -> None:
    default_table_list = list(DEFAULT_TABLE_SCHEMA.keys())
    updated_table = _update_table_with_new_consistent_row(
        fresh_db, default_table_list[0]
    )

    fresh_db.write_tables_to_csv(default_table_list[0:1])
    written_table = parse_datetime_columns(
        pd.read_csv(f"{tmp_path}/{default_table_list[0]}.csv")
    )

    assert updated_table.equals(written_table)


def test_write_tables_to_csv_all_tables(fresh_db: DB, tmp_path: Path) -> None:
    updated_tables: dict[str, pd.DataFrame] = {}
    default_table_list = list(DEFAULT_TABLE_SCHEMA.keys())
    for table_name in default_table_list:
        updated_tables[table_name] = _update_table_with_new_consistent_row(
            fresh_db, table_name
        )

    fresh_db.write_tables_to_csv()
    for table_name in default_table_list:
        written_table = parse_datetime_columns(
            pd.read_csv(f"{tmp_path}/{table_name}.csv")
        )
        assert updated_tables[table_name].equals(written_table)


def test_write_tables_to_csv_invalid_table_name(
    fresh_db: DB, random_string: Callable[[int], str]
) -> None:
    with pytest.raises(ValueError):
        fresh_db.write_tables_to_csv([random_string(20)])


def _update_table_with_new_consistent_row(
    fresh_db: DB, table_name: str
) -> pd.DataFrame:
    current_table = fresh_db.get_db().sql(f"SELECT * FROM {table_name}").df()

    new_row = get_random_consistent_row(current_table)
    fresh_db.get_db().sql(f"""
        INSERT INTO {table_name}
        VALUES ({", ".join([f"'{str(new_row[v])}'" for v in current_table.columns])})
    """)

    updated_table = pd.concat(
        [current_table, pd.DataFrame([new_row])], ignore_index=True
    )
    return updated_table


def _cast_all_columns_to_strings(df: pd.DataFrame) -> None:
    for col in df.columns:
        df[col] = df[col].astype(str)
