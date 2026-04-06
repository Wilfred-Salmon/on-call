from src.rota.rotas import add_user_to_rota_on_date

import pytest
from datetime import date, timedelta
from src.util.list_util import cycle_list
from src.util.date_util import get_first_monday_before_date
from test.helpers import (
    DBFactory,
    DBSpecification,
    change_timestamps_to_dates,
    snapshot_tables_from_specification,
)

NEW_USER_NAME = "new_user"


@pytest.mark.parametrize(
    "new_date",
    [date(2026, 1, 5), date(2026, 1, 11), date(2026, 1, 12), date(2026, 1, 18)],
    ids=["monday_before", "sunday_before", "monday_of", "sunday_of"],
)
def test_add_user_to_rota_on_date_fails_with_future_snapshots(
    new_date: date, custom_db: DBFactory
) -> None:
    custom_db_specification: DBSpecification = {
        "rota_1": [{"date": date(2026, 1, 12), "user_list": [NEW_USER_NAME]}]
    }
    with custom_db(custom_db_specification) as db:
        with pytest.raises(ValueError):
            add_user_to_rota_on_date(user_id=0, rota_id=0, date=new_date, db=db)


@pytest.mark.parametrize(
    "offset,expected_cycle",
    [(7, 1), (8, 1), (14, 2), (15, 2)],
    ids=["1_week", "1_week_and_1_day", "2_weeks", "2_weeks_and_1_day"],
)
def test_add_user_to_rota_on_date(
    offset: int, expected_cycle: int, custom_db: DBFactory
) -> None:
    initial_date = date(2026, 1, 12)
    initial_user_list = sorted(["user_1", "user_2"])

    custom_db_specification: DBSpecification = {
        "rota_1": [{"date": initial_date, "user_list": initial_user_list}]
    }
    with custom_db(custom_db_specification) as db:
        add_user_to_rota_on_date(
            user_id=2, rota_id=0, date=initial_date + timedelta(days=offset), db=db
        )

        snapshot_table = (
            db.get_db()
            .sql("SELECT * FROM rota_snapshots")
            .fetchdf()
            .to_dict(orient="records")
        )
        change_date_table = (
            db.get_db()
            .sql("SELECT * FROM change_dates")
            .fetchdf()
            .to_dict(orient="records")
        )
        change_timestamps_to_dates(change_date_table)

        custom_db_specification["rota_1"].append(
            {
                "date": get_first_monday_before_date(
                    initial_date + timedelta(days=offset)
                ),
                "user_list": [NEW_USER_NAME]
                + cycle_list(initial_user_list, expected_cycle),
            }
        )

        expected_change_date_table, expected_snapshot_table = (
            snapshot_tables_from_specification(
                custom_db_specification,
                user_id_dict={"user_1": 0, "user_2": 1, NEW_USER_NAME: 2},
                rota_id_dict={"rota_1": 0},
            )
        )
        assert expected_snapshot_table == snapshot_table
        assert expected_change_date_table == change_date_table
