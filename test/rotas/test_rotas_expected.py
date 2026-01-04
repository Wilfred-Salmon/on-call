from src.rota.interval import Interval
from datetime import date

EXPECTED_NO_OVERRIDES_1 = [
    {"start_date": date(2025,1,6), "end_date": date(2025,1,13), "user": "Harry"},
    {"start_date": date(2025,1,13), "end_date": date(2025,1,20), "user": "Harry"},
    {"start_date": date(2025,1,20), "end_date": date(2025,1,27), "user": "Harry"},
    {"start_date": date(2025,1,27), "end_date": date(2025,2,3), "user": "Harry"},
    {"start_date": date(2025,2,3), "end_date": date(2025,2,10), "user": "Harry"},
    {"start_date": date(2025,2,10), "end_date": date(2025,2,17), "user": "Harry"},
    {"start_date": date(2025,2,17), "end_date": date(2025,2,24), "user": "Harry"},
    {"start_date": date(2025,2,24), "end_date": date(2025,3,3), "user": "Harry"},
    {"start_date": date(2025,3,3), "end_date": date(2025,3,10), "user": "Ron"},
    {"start_date": date(2025,3,10), "end_date": date(2025,3,17), "user": "Ron"},
    {"start_date": date(2025,3,17), "end_date": date(2025,3,24), "user": "Harry"},
    {"start_date": date(2025,3,24), "end_date": date(2025,3,31), "user": "Hermione"},
    {"start_date": date(2025,3,31), "end_date": date(2025,4,7), "user": "Ron"},
    {"start_date": date(2025,4,7), "end_date": date(2025,4,14), "user": "Harry"},
    {"start_date": date(2025,4,14), "end_date": date(2025,4,21), "user": "Hermione"},
    {"start_date": date(2025,4,21), "end_date": date(2025,4,28), "user": "Ron"},
]

EXPECTED_NO_OVERRIDES_2 = [
    {"start_date": date(2025,2,3), "end_date": date(2025,2,10), "user": "Harry"}
]

EXPECTED_NO_OVERRIDES_3 = [
    {"start_date": date(2025,1,6), "end_date": date(2025,1,13), "user": "Harry"}
]

EXPECTED_NO_OVERRIDES_4 = []