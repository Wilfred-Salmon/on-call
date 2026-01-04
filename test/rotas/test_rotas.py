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
        (date(2025,1,8), date(2025, 1, 7), EXPECTED_NO_OVERRIDES_5),
        (date(2025,2,8), date(2025, 1, 8), EXPECTED_NO_OVERRIDES_6)
    ],
    ids = ["Long Query", "No expansion", "before rota start to within rota", "fully before rota start", "end date before start date, fixed by expansion", "end date before start date, not fixed by expansion"]
)
def test_get_rota_between_without_overrides(shared_db, start_date, end_date, expected):
    actual = get_rota_between(start_date, end_date, 0, shared_db)

    assert actual == expected