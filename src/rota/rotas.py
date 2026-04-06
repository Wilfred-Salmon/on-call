from datetime import date
from duckdb import DuckDBPyConnection
from src.db.db import DB
from src.util.date_util import (
    add_week,
    get_first_monday_before_date,
    get_next_sunday_after_date,
)
from src.util.list_util import get_cyclical_list_iterator, cycle_list
from typing import TypedDict
from pydantic import BaseModel


# TODO: make dataclass instead of typed dict?
class Snapshot_with_usernames(TypedDict):
    date: date
    user_list: list[str]


class _Snapshot_with_user_ids(TypedDict):
    date: date
    user_list: list[int]


class Rota_Assignment(BaseModel):
    start_date: date
    end_date: date
    user: str


def get_rota_between(
    start_date: date, end_date: date, rota_id: int, db: DuckDBPyConnection
) -> list[Rota_Assignment]:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")

    start_date = get_first_monday_before_date(start_date)
    end_date = get_next_sunday_after_date(end_date)

    snapshots = _get_rota_snapshots_between(rota_id, start_date, end_date, db)
    weekly_rota = _expand_snapshots_to_full_weeks(snapshots, start_date, end_date)

    # TODO: apply_overrides()

    return weekly_rota


def _get_rota_snapshots_between(
    rota_id: int, start_date: date, end_date: date, db: DuckDBPyConnection
) -> list[Snapshot_with_usernames]:
    snapshot_records = (
        db.sql(f"""
        SELECT d.date, LIST(u.name ORDER BY s.index) as user_list
        FROM change_dates d
        LEFT JOIN rota_snapshots s
            ON s.snapshot_id = d.snapshot_id
        LEFT JOIN users u
            ON u.user_id = s.user_id
        WHERE d.rota_id = {rota_id}
            AND d.date BETWEEN
            COALESCE(
                (SELECT MAX(d.date)
                FROM change_dates d
                WHERE d.date <= '{str(start_date)}'
                    AND d.rota_id = {rota_id}),
                '{str(start_date)}'
            ) AND '{str(end_date)}'
        GROUP BY d.date
        ORDER BY d.date
    """)
        .df()
        .to_dict(orient="records")
    )

    snapshots: list[Snapshot_with_usernames] = [
        {"date": r["date"].date(), "user_list": r["user_list"]}
        for r in snapshot_records
    ]

    return snapshots


def _get_last_rota_snapshot_before_date(
    rota_id: int, date: date, db: DuckDBPyConnection
) -> _Snapshot_with_user_ids | None:
    # TODO: think of a better way to do this, without the COALESCE FILTER thing. Wrap all SQL queries like this?
    snapshot_records = (
        db.sql(f"""
        SELECT d.date, COALESCE(LIST(s.user_id ORDER BY s.index) FILTER (WHERE s.user_id IS NOT NULL), []) as user_list
        FROM change_dates d
        LEFT JOIN rota_snapshots s
            ON s.snapshot_id = d.snapshot_id
        WHERE d.rota_id = {rota_id}
            AND d.date <= '{str(date)}'
        GROUP BY d.date
        ORDER BY d.date DESC
        LIMIT 1
    """)
        .df()
        .to_dict(orient="records")
    )
    if len(snapshot_records) == 0:
        return None

    snapshot = snapshot_records[0]
    return {"date": snapshot["date"].date(), "user_list": snapshot["user_list"]}


def _snapshots_exist_on_or_after_date(
    rota_id: int, date: date, db: DuckDBPyConnection
) -> bool:
    snapshot_records = (
        db.sql(f"""
        SELECT 1
        FROM change_dates d
        WHERE d.rota_id = {rota_id}
            AND d.date >= '{str(date)}'
        LIMIT 1
    """)
        .df()
        .to_dict(orient="records")
    )
    return len(snapshot_records) > 0


def _expand_snapshots_to_full_weeks(
    snapshots: list[Snapshot_with_usernames], start_date: date, end_date: date
) -> list[Rota_Assignment]:
    if len(snapshots) == 0:
        return []

    rota: list[Rota_Assignment] = []

    it_snapshots = iter(snapshots)
    current_snapshot = next(it_snapshots)
    _DUMMY_SNAPSHOT = Snapshot_with_usernames({"date": date.max, "user_list": []})
    next_snapshot = next(it_snapshots, _DUMMY_SNAPSHOT)

    current_date = max(start_date, current_snapshot["date"])
    current_user_ordering = get_cyclical_list_iterator(current_snapshot["user_list"])

    while current_date < end_date:
        if current_date >= next_snapshot["date"]:
            current_snapshot = next_snapshot
            current_user_ordering = get_cyclical_list_iterator(
                current_snapshot["user_list"]
            )
            next_snapshot = next(it_snapshots, _DUMMY_SNAPSHOT)

        rota.append(
            Rota_Assignment(
                start_date=current_date,
                end_date=add_week(current_date),
                user=next(current_user_ordering),
            )
        )

        current_date = add_week(current_date)

    return rota


def add_user_to_rota_on_date(user_id: int, rota_id: int, date: date, db: DB) -> None:
    date = get_first_monday_before_date(date)
    if _snapshots_exist_on_or_after_date(rota_id, date, db.get_db()):
        raise ValueError(
            f"Cannot add user on {date} to rota {rota_id}, as there are changes after that date"
        )

    latest_snapshot = _get_last_rota_snapshot_before_date(rota_id, date, db.get_db())
    new_user_list = _get_new_user_list(user_id, date, latest_snapshot)

    _add_new_rota_snapshot_to_db(rota_id, new_user_list, date, db.get_db())
    db.write_tables_to_csv(["change_dates", "rota_snapshots"])


def _get_new_user_list(
    user_id: int, date: date, latest_snapshot: _Snapshot_with_user_ids | None
) -> list[int]:
    if latest_snapshot is None or len(latest_snapshot["user_list"]) == 0:
        new_user_list = [user_id]
    else:
        latest_snaphost_valid_on = latest_snapshot["date"]
        offset = (date - latest_snaphost_valid_on).days // 7

        latest_snapshot_user_list = latest_snapshot["user_list"]
        new_user_list = [user_id] + cycle_list(latest_snapshot_user_list, offset)
    return new_user_list


def _add_new_rota_snapshot_to_db(
    rota_id: int, user_list: list[int], date: date, db: DuckDBPyConnection
) -> None:
    snapshot_id = _add_new_change_date_to_db(rota_id, date, db)
    insert_query = f"""
        INSERT INTO rota_snapshots
        VALUES {",\n".join(f"({snapshot_id}, {user_id}, {i})" for i, user_id in enumerate(user_list))}
    """
    db.sql(insert_query)


def _add_new_change_date_to_db(rota_id: int, date: date, db: DuckDBPyConnection) -> int:
    new_id_row = db.sql(
        "SELECT COALESCE(MAX(snapshot_id), 0) + 1 AS new_id FROM change_dates"
    ).fetchone()
    assert (
        new_id_row is not None
    )  # Needed to satisfy type checker, but should never be None because of COALESCE in the query

    new_id = new_id_row[0]
    db.sql(f"""
        INSERT INTO change_dates
        VALUES ({rota_id},'{str(date)}', {new_id})
    """)
    return new_id
