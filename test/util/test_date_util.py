import pytest
from src.util.date_util import *
from types import SimpleNamespace
from datetime import date

@pytest.fixture(scope="module")
def simple_dates():
    return SimpleNamespace(
        MONDAY = date(2025, 11, 17),
        WEDNESDAY = date(2025, 11, 19),
        SUNDAY = date(2025, 11, 23),
        FOLLOWING_MONDAY = date(2025, 11, 24)
    )

def test_get_next_sunday_after_date_on_midweek(simple_dates):
    assert get_next_sunday_after_date(simple_dates.WEDNESDAY) == simple_dates.SUNDAY

def test_get_next_sunday_after_date_on_sunday(simple_dates):
    assert get_next_sunday_after_date(simple_dates.SUNDAY) == simple_dates.SUNDAY

def test_get_first_monday_before_date_on_monday(simple_dates):
    assert get_first_monday_before_date(simple_dates.MONDAY) == simple_dates.MONDAY

def test_get_first_monday_before_date_on_midweek(simple_dates):
    assert get_first_monday_before_date(simple_dates.WEDNESDAY) == simple_dates.MONDAY

def test_add_week(simple_dates):
    assert add_week(simple_dates.MONDAY) == simple_dates.FOLLOWING_MONDAY