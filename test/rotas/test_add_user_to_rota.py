from src.rota.rotas import add_user_to_rota_on_date
from src.db.db import DB

import pytest
from typing import Callable
from datetime import date
from test.helpers import DBSpecification


@pytest.mark.parametrize(
    "new_date",
    [date(2026, 1, 5), date(2026, 1, 11), date(2026, 1, 12), date(2026, 1, 18)],
    ids=["monday_before", "sunday_before", "monday_of", "sunday_of"],
)
def test_add_user_to_rota_on_date_fails_with_future_snapshots(
    new_date: date, custom_db: Callable[[DBSpecification], DB]
) -> None:
    custom_db_specification: DBSpecification = {
        "rota_1": [{"date": date(2026, 1, 12), "user_list": ["user_1"]}]
    }
    # mypy gets confused with pytest handling the context managers
    with custom_db(custom_db_specification) as db:  # type: ignore[attr-defined]
        with pytest.raises(ValueError):
            add_user_to_rota_on_date(user_id=0, rota_id=0, date=new_date, db=db)


def test_add_user_to_rota_on_date() -> None:
    pass
