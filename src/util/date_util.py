from datetime import date, timedelta

def get_next_sunday_after_date(
    date: date
) -> date:
    shift = (6 - date.weekday()) % 7
    return date + timedelta(shift)

def get_first_monday_before_date(
    date: date
) -> date:
    shift = -date.weekday()
    return date + timedelta(shift)

def add_week(
    date: date
) -> date:
    return date + timedelta(7)