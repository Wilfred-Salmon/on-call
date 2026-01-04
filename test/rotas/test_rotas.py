import pytest
from src.rotas import get_rota_between
from datetime import date
from test_rotas_expected import *

@pytest.mark.parametrize(
    "start_date, end_date, expected", 
    [
        (date(2025,1,7), date(2025, 4, 22), EXPECTED_NO_OVERRIDES_1),
        (date(2025,2,3), date(2025, 2, 9), EXPECTED_NO_OVERRIDES_2),
        (date(2024,1,1), date(2025, 1, 6), EXPECTED_NO_OVERRIDES_3),
        (date(2024,1,1), date(2024, 6, 1), EXPECTED_NO_OVERRIDES_4),
    ],
    ids = ["Long Query", "No expansion", "before rota start to within rota", "fully before rota start"]
)
def test_get_rota_between_without_overrides(shared_db, start_date, end_date, expected):
    actual = get_rota_between(start_date, end_date, 0, shared_db)

    assert actual == expected

@pytest.mark.parametrize(
    "start_date, end_date", 
    [
        (date(2025,1,8), date(2025, 1, 7)),
        (date(2025,2,8), date(2025, 1, 8))
    ],
    ids = ["end date before start date, fixed by expansion", "end date before start date, not fixed by expansion"]
)
def test_get_rota_between_invalid_dates(start_date, end_date, shared_db):
    with pytest.raises(ValueError):
        get_rota_between(start_date, end_date, 0, shared_db)

def test_get_rota_between_invalid_rota_id(shared_db):
    actual = get_rota_between(date(2025,1,1), date(2025,1,1), 1000, shared_db)
    assert actual == []