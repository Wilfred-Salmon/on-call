from datetime import date, timedelta
from .interval import Interval
from typing import TypedDict, TypeVar
import duckdb as db
import pandas as pd

def load_db(
    table_list: list[str], 
    root_fp: str
) -> None:
    for table in table_list:
        db.register(table, db.read_csv(f"{root_fp}/{table}.csv"))

class _Snapshot(TypedDict):
    date: date
    user_list: list[str]

def get_on_call_between(
    start_date: date,
    end_date: date,
    rota_id: int
) -> list[dict[Interval, str]]:
    start_date = _get_first_monday_before_date(start_date)
    end_date = _get_next_sunday_after_date(end_date)

    snapshots = _get_rota_snapshots_between(rota_id, start_date, end_date)
    weekly_rota = _expand_snapshots_to_full_weeks(snapshots, start_date, end_date)

    # apply_overrides()

    return weekly_rota

def _get_rota_snapshots_between(
    rota_id: int,
    start_date: date,
    end_date: date
) -> list[_Snapshot]:
    snapshot_records =  db.sql(f"""
        SELECT d.date, LIST(u.name ORDER BY s.index) as user_list
        FROM change_dates d
        LEFT JOIN rota_snapshots s
            ON s.snapshot_id = d.snapshot_id
        LEFT JOIN users u
            ON u.user_id = s.user_id
        WHERE d.rota_id = {rota_id}
            AND d.date <= '{str(end_date)}'
            AND d.date >= '{str(start_date)}'
        GROUP BY d.date
        ORDER BY d.date
    """).df().to_dict(orient="records")

    snapshots: list[_Snapshot] = [{"date": r["date"].date(), "user_list": r["user_list"]} for r in snapshot_records]

    return snapshots

def _expand_snapshots_to_full_weeks(
    snapshots: list[_Snapshot], 
    start_date: date, 
    end_date: date
) -> list[dict[Interval, str]]:
    if len(snapshots) == 0:
        return []
    
    snapshots.append({'date': date.max, 'user_list': []})
    it_snapshots = iter(snapshots)

    rota = []
    
    current_snapshot = next(it_snapshots)
    next_snapshot = next(it_snapshots)
    current_date = max(start_date, current_snapshot['date'])

    while current_date < end_date:
        if current_date >= next_snapshot['date']:
            current_snapshot = next_snapshot
            next_snapshot = next(it_snapshots)

        shift = (current_date - current_snapshot['date']).days // 7
        user = _get_at_index_with_wrap(current_snapshot['user_list'], shift)

        rota.append({Interval(current_date, _add_week(current_date)): user})

        current_date = _add_week(current_date)       

    return rota

def _get_next_sunday_after_date(
    date: date
) -> date:
    shift = (6 - date.weekday()) % 7
    return date + timedelta(shift)

def _get_first_monday_before_date(
    date: date
) -> date:
    shift = -date.weekday()
    return date + timedelta(shift)

def _add_week(
    date: date
) -> date:
    return date + timedelta(7)

T = TypeVar('T')

def _get_at_index_with_wrap(
    list: list[T],
    index: int
) -> T:
    return list[index % len(list)]
