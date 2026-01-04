from src.interval import Interval
from datetime import date

EXPECTED_NO_OVERRIDES_1 = [
    {Interval(date(2025,1,6), date(2025,1,13)): "Harry"},
    {Interval(date(2025,1,13), date(2025,1,20)): "Harry"},
    {Interval(date(2025,1,20), date(2025,1,27)): "Harry"},
    {Interval(date(2025,1,27), date(2025,2,3)): "Harry"},
    {Interval(date(2025,2,3), date(2025,2,10)): "Harry"},
    {Interval(date(2025,2,10), date(2025,2,17)): "Harry"},
    {Interval(date(2025,2,17), date(2025,2,24)): "Harry"},
    {Interval(date(2025,2,24), date(2025,3,3)): "Harry"},
    {Interval(date(2025,3,3), date(2025,3,10)): "Ron"},
    {Interval(date(2025,3,10), date(2025,3,17)): "Ron"},
    {Interval(date(2025,3,17), date(2025,3,24)): "Harry"},
    {Interval(date(2025,3,24), date(2025,3,31)): "Hermione"},
    {Interval(date(2025,3,31), date(2025,4,7)): "Ron"},
    {Interval(date(2025,4,7), date(2025,4,14)): "Harry"},
    {Interval(date(2025,4,14), date(2025,4,21)): "Hermione"},
    {Interval(date(2025,4,21), date(2025,4,28)): "Ron"},
]

EXPECTED_NO_OVERRIDES_2 = [
    {Interval(date(2025,2,3), date(2025,2,10)): "Harry"}
]