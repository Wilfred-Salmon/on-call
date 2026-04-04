import pandas as pd
import numpy as np
from typing import Any, Hashable

def get_random_consistent_row(df: pd.DataFrame) -> dict[Hashable, Any]:
    row: dict[Hashable, Any] = {}
    for col, dtype in df.dtypes.items():
        if pd.api.types.is_integer_dtype(dtype):
            row[col] = np.random.randint(1, 100)
        elif pd.api.types.is_string_dtype(dtype):
            row[col] = f"test_string_{np.random.randint(0, 100)}"
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            if all(df[col].dt.normalize() == df[col]): # If all value are dates, insert a date
                row[col] = pd.Timestamp.now().normalize() + pd.Timedelta(days = np.random.randint(0, 30))
            else:
                row[col] = pd.Timestamp.now() + pd.Timedelta(days = np.random.randint(0, 30))
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