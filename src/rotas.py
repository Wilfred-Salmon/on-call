from datetime import date
from duckdb import DuckDBPyConnection
from .interval import Interval
from .util.date_util import add_week, get_first_monday_before_date, get_next_sunday_after_date
from .util.list_util import get_at_index_with_wrap
from typing import TypedDict

# TODO: make dataclass instead of typed dict?
class _Snapshot(TypedDict):
    date: date
    user_list: list[str]

def get_rota_between(
    start_date: date,
    end_date: date,
    rota_id: int,
    db: DuckDBPyConnection
) -> list[dict[Interval, str]]:
    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")
    
    start_date = get_first_monday_before_date(start_date)
    end_date = get_next_sunday_after_date(end_date)

    snapshots = _get_rota_snapshots_between(rota_id, start_date, end_date, db)
    weekly_rota = _expand_snapshots_to_full_weeks(snapshots, start_date, end_date)

    # TODO: apply_overrides()

    return weekly_rota

def _get_rota_snapshots_between(
    rota_id: int,
    start_date: date,
    end_date: date,
    db: DuckDBPyConnection
) -> list[_Snapshot]:
    snapshot_records =  db.sql(f"""
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
        user = get_at_index_with_wrap(current_snapshot['user_list'], shift)

        rota.append({Interval(current_date, add_week(current_date)): user})

        current_date = add_week(current_date)       

    return rota