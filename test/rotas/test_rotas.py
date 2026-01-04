import pytest
from src.rota.rotas import get_rota_between
from src.rota.interval import Interval
from datetime import date
from test_rotas_expected import *
from duckdb import DuckDBPyConnection

@pytest.mark.parametrize(
    "start_date, end_date, rota_index, expected", 
    [
        (date(2025,1,7), date(2025, 4, 22), 0, EXPECTED_NO_OVERRIDES_1),
        (date(2025,2,3), date(2025, 2, 9), 0, EXPECTED_NO_OVERRIDES_2),
        (date(2024,1,1), date(2025, 1, 6), 0, EXPECTED_NO_OVERRIDES_3),
        (date(2024,1,1), date(2024, 6, 1), 0, EXPECTED_NO_OVERRIDES_4),
    ],
    ids = ["Long Query", "No expansion", "before rota start to within rota", "fully before rota start"]
)
def test_get_rota_between_without_overrides(
    shared_db: DuckDBPyConnection, 
    start_date: date,
    end_date: date, 
    rota_index: int, 
    expected: list[dict[Interval, str]]
):
    actual = get_rota_between(start_date, end_date, rota_index, shared_db)

    assert actual == expected

@pytest.mark.parametrize(
    "start_date, end_date, rota_index", 
    [
        (date(2025,1,8), date(2025, 1, 7), 0),
        (date(2025,2,8), date(2025, 1, 8), 0)
    ],
    ids = ["end date before start date, fixed by expansion", "end date before start date, not fixed by expansion"]
)
def test_get_rota_between_invalid_dates(
    shared_db: DuckDBPyConnection,
    start_date: date, 
    end_date: date, 
    rota_index: int
):
    with pytest.raises(ValueError):
        get_rota_between(start_date, end_date, rota_index, shared_db)

def test_get_rota_between_invalid_rota_id(
    shared_db: DuckDBPyConnection, 
    invalid_rota_id = 1000
):
    actual = get_rota_between(date(2025,1,1), date(2025,1,1), invalid_rota_id, shared_db)
    assert actual == []