from contextlib import AbstractContextManager

import pandas as pd
import numpy as np
from typing import Any, Callable, Hashable, TypedDict

from src.db.db import DB
from src.rota.rotas import Snapshot_with_usernames
from datetime import date

type DBSpecification = dict[str, list[Snapshot_with_usernames]]
type DBFactory = Callable[[DBSpecification], AbstractContextManager[DB]]


class RawSnapshot(TypedDict):
    snapshot_id: int
    user_id: int
    index: int


class RawChangeDate(TypedDict):
    rota_id: int
    date: date
    snapshot_id: int


def get_random_consistent_row(df: pd.DataFrame) -> dict[Hashable, Any]:
    row: dict[Hashable, Any] = {}
    for col, dtype in df.dtypes.items():
        if pd.api.types.is_integer_dtype(dtype):
            row[col] = np.random.randint(1, 100)
        elif pd.api.types.is_string_dtype(dtype):
            row[col] = f"test_string_{np.random.randint(0, 100)}"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            if all(
                df[col].dt.normalize() == df[col]
            ):  # If all value are dates, insert a date
                row[col] = pd.Timestamp.now().normalize() + pd.Timedelta(
                    days=np.random.randint(0, 30)
                )
            else:
                row[col] = pd.Timestamp.now() + pd.Timedelta(
                    days=np.random.randint(0, 30)
                )
        elif pd.api.types.is_float_dtype(dtype):
            row[col] = np.random.rand()
        else:
            raise ValueError(f"Unsupported dtype: {dtype}")
    return row


def parse_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            converted = pd.to_datetime(df[col], errors="coerce")
            if converted.notna().sum() == len(df):
                df[col] = converted
    return df


def construct_default_user_table(user_names_list: list[str]) -> dict[str, int]:
    return {user_name: i for i, user_name in enumerate(set(user_names_list))}


def snapshot_tables_from_specification(
    db_specification: DBSpecification,
    user_table: dict[str, int],
    rota_table: dict[str, int],
) -> tuple[list[RawChangeDate], list[RawSnapshot]]:
    snapshot_id = 0
    change_dates = []
    rota_snapshots = []
    for rota, snapshots in db_specification.items():
        for snapshot in snapshots:
            change_dates.append(
                RawChangeDate(
                    {
                        "rota_id": rota_table[rota],
                        "date": snapshot["date"],
                        "snapshot_id": snapshot_id,
                    }
                )
            )
            for index, user_name in enumerate(snapshot["user_list"]):
                rota_snapshots.append(
                    RawSnapshot(
                        {
                            "snapshot_id": snapshot_id,
                            "user_id": user_table[user_name],
                            "index": index,
                        }
                    )
                )
            snapshot_id += 1
    return change_dates, rota_snapshots


def get_full_table(
    db: DB, table_name: str, make_timestamps_dates: bool = True
) -> list[dict[Hashable, Any]]:
    raw_records = (
        db.get_db()
        .sql(f"SELECT * FROM {table_name}")
        .fetchdf()
        .to_dict(orient="records")
    )
    if make_timestamps_dates:
        _change_timestamps_to_dates(raw_records)
    return raw_records


def _change_timestamps_to_dates(records: list[dict[Hashable, Any]]) -> None:
    for record in records:
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                record[key] = value.to_pydatetime().date()
