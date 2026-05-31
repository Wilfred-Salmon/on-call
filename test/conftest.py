from contextlib import contextmanager
from pathlib import Path
import random
import string
from typing import Callable, Generator
from datetime import date

import pytest
import shutil
import pandas as pd
from src.db.db import DB, DEFAULT_TABLE_SCHEMA
from test.helpers import (
    DBFactory,
    DBSpecification,
    RawChangeDate,
    RawSnapshot,
    snapshot_tables_from_specification,
    construct_default_user_table,
)

SHARED_DB_PATH = Path("./test/test_db_data")
DEFAULT_DB_SPECIFICATION: DBSpecification = {
    "potion_brewing": [
        {"date": date(2025, 1, 6), "user_list": ["Harry"]},
        {"date": date(2025, 3, 3), "user_list": ["Ron", "Harry"]},
        {"date": date(2025, 3, 10), "user_list": ["Ron", "Harry", "Hermione"]},
    ],
    "gnoming": [{"date": date(2025, 2, 3), "user_list": ["Harry", "Neville"]}],
}
DEFAULT_USER_TABLE = {"Harry": 0, "Ron": 1, "Hermione": 2, "Neville": 3}
DEFAULT_ROTA_TABLE = {"potion_brewing": 0, "gnoming": 1}


@pytest.fixture(scope="session")
def random_string() -> Callable[[int], str]:
    def _random_string(length: int) -> str:
        return "".join(random.choices(string.ascii_letters, k=length))

    return _random_string


def fresh_db_with_rotas(
    path: Path,
    db_specification: DBSpecification,
    user_table: dict[str, int] | None = None,
    rota_table: dict[str, int] | None = None,
) -> Generator[DB]:
    if user_table is None:
        user_names_list = sorted(_get_user_names(db_specification))
        user_table = construct_default_user_table(user_names_list)
    rota_table = rota_table or construct_default_rota_table(db_specification)

    change_dates, rota_snapshots = snapshot_tables_from_specification(
        db_specification, user_table, rota_table
    )

    _write_db_tables(path, user_table, rota_table, change_dates, rota_snapshots)

    db = DB(DEFAULT_TABLE_SCHEMA, str(path))
    yield db
    db.close()


def construct_default_rota_table(db_specification: DBSpecification) -> dict[str, int]:
    return {name: i for i, name in enumerate(sorted(db_specification.keys()))}


def _write_db_tables(
    path: Path,
    user_table: dict[str, int],
    rota_table: dict[str, int],
    change_dates: list[RawChangeDate],
    rota_snapshots: list[RawSnapshot],
) -> None:
    pd.DataFrame(change_dates, columns=["rota_id", "date", "snapshot_id"]).to_csv(
        path / "change_dates.csv", index=False
    )
    pd.DataFrame(rota_snapshots, columns=["snapshot_id", "user_id", "index"]).to_csv(
        path / "rota_snapshots.csv", index=False
    )
    pd.DataFrame(
        [(id, name) for name, id in user_table.items()], columns=["user_id", "name"]
    ).to_csv(path / "users.csv", index=False)
    pd.DataFrame(
        [(id, name) for name, id in rota_table.items()], columns=["rota_id", "name"]
    ).to_csv(path / "rota_names.csv", index=False)
    pd.DataFrame([], columns=["user_id", "rota_id", "start_date", "duration"]).to_csv(
        path / "overrides.csv", index=False
    )


def _get_user_names(db_specification: DBSpecification) -> list[str]:
    user_names_list = list(
        set(
            [
                user_name
                for user_list in [
                    snapshot["user_list"]
                    for snaphot_list in db_specification.values()
                    for snapshot in snaphot_list
                ]
                for user_name in user_list
            ]
        )
    )

    return user_names_list


@pytest.fixture(scope="session")
def shared_db() -> Generator[DB]:
    SHARED_DB_PATH.mkdir(exist_ok=False)
    yield from fresh_db_with_rotas(
        SHARED_DB_PATH, DEFAULT_DB_SPECIFICATION, DEFAULT_USER_TABLE, DEFAULT_ROTA_TABLE
    )
    shutil.rmtree(SHARED_DB_PATH, ignore_errors=True)


@pytest.fixture()
def fresh_db(tmp_path: Path) -> Generator[DB]:
    yield from fresh_db_with_rotas(
        tmp_path, DEFAULT_DB_SPECIFICATION, DEFAULT_USER_TABLE, DEFAULT_ROTA_TABLE
    )


@pytest.fixture()
def custom_db(tmp_path: Path) -> DBFactory:
    @contextmanager
    def _custom_db(
        db_specification: DBSpecification,
        user_table: dict[str, int] | None = None,
        rota_table: dict[str, int] | None = None,
    ) -> Generator[DB]:
        yield from fresh_db_with_rotas(
            tmp_path, db_specification, user_table, rota_table
        )

    return _custom_db
