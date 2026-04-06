from src.rota.rotas import add_user_to_rota_on_date

import pytest
from datetime import date, timedelta
from src.util.list_util import cycle_list
from src.util.date_util import get_first_monday_before_date
from test.helpers import (
    DBFactory,
    DBSpecification,
    get_full_table,
    snapshot_tables_from_specification,
    construct_default_user_table,
)

NEW_USER_NAME = "new_user"
INITIAL_ROTA_NAME = "rota_1"
INITIAL_SNAPSHOT_DATE = date(2026, 1, 12)


@pytest.mark.parametrize(
    "new_date",
    [date(2026, 1, 5), date(2026, 1, 11), date(2026, 1, 12), date(2026, 1, 18)],
    ids=["monday_before", "sunday_before", "monday_of", "sunday_of"],
)
def test_add_user_to_rota_on_date_fails_with_future_snapshots(
    new_date: date, custom_db: DBFactory
) -> None:
    custom_db_specification: DBSpecification = {
        INITIAL_ROTA_NAME: [
            {"date": INITIAL_SNAPSHOT_DATE, "user_list": [NEW_USER_NAME]}
        ]
    }
    with custom_db(custom_db_specification) as db:
        with pytest.raises(ValueError):
            add_user_to_rota_on_date(user_id=0, rota_id=0, date=new_date, db=db)


@pytest.mark.parametrize(
    "offset,expected_cycle",
    [(7, 1), (8, 1), (14, 2), (15, 2)],
    ids=["1_week", "1_week_and_1_day", "2_weeks", "2_weeks_and_1_day"],
)
@pytest.mark.parametrize(
    "initial_user_list",
    [(["user_1"]), (["user_1", "user_2"])],
    ids=["one_user", "two_users"],
)
def test_add_user_to_rota_on_date(
    offset: int, expected_cycle: int, initial_user_list: list[str], custom_db: DBFactory
) -> None:
    initial_user_list = sorted(initial_user_list)

    custom_db_specification: DBSpecification = {
        INITIAL_ROTA_NAME: [
            {"date": INITIAL_SNAPSHOT_DATE, "user_list": initial_user_list}
        ]
    }
    with custom_db(custom_db_specification) as db:
        add_user_to_rota_on_date(
            user_id=len(initial_user_list),
            rota_id=0,
            date=INITIAL_SNAPSHOT_DATE + timedelta(days=offset),
            db=db,
        )

        snapshot_table = get_full_table(db, "rota_snapshots")
        change_date_table = get_full_table(db, "change_dates")

        custom_db_specification["rota_1"].append(
            {
                "date": get_first_monday_before_date(
                    INITIAL_SNAPSHOT_DATE + timedelta(days=offset)
                ),
                "user_list": [NEW_USER_NAME]
                + cycle_list(initial_user_list, expected_cycle),
            }
        )

        expected_change_date_table, expected_snapshot_table = (
            snapshot_tables_from_specification(
                custom_db_specification,
                user_table=construct_default_user_table(initial_user_list)
                | {NEW_USER_NAME: len(initial_user_list)},
                rota_table={INITIAL_ROTA_NAME: 0},
            )
        )
        assert expected_snapshot_table == snapshot_table
        assert expected_change_date_table == change_date_table
