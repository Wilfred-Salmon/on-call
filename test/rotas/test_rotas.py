import pytest
from src.rotas import get_rota_between
from datetime import date
from test_rotas_expected import *


@pytest.mark.parametrize(
    "start_date, end_date, expected", 
    [
        (date(2025,1,7), date(2025, 4, 22), EXPECTED_NO_OVERRIDES_1),
        (date(2025,2,3), date(2025, 2, 9), EXPECTED_NO_OVERRIDES_2)
    ],
    ids = ["Long Query", "No expansion"]
)
def test_get_rota_between_without_overrides(shared_db, start_date, end_date, expected):
    actual = get_rota_between(start_date, end_date, 0, shared_db)

    assert actual == expected