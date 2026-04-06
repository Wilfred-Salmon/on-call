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


def snapshot_tables_from_specification(
    db_specification: DBSpecification,
    user_id_dict: dict[str, int],
    rota_id_dict: dict[str, int],
) -> tuple[list[RawChangeDate], list[RawSnapshot]]:
    snapshot_id = 0
    change_dates = []
    rota_snapshots = []
    for rota, snapshots in db_specification.items():
        for snapshot in snapshots:
            change_dates.append(
                RawChangeDate(
                    {
                        "rota_id": rota_id_dict[rota],
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
                            "user_id": user_id_dict[user_name],
                            "index": index,
                        }
                    )
                )
            snapshot_id += 1
    return change_dates, rota_snapshots


def change_timestamps_to_dates(records: list[dict[Hashable, Any]]) -> None:
    for record in records:
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                record[key] = value.to_pydatetime().date()
