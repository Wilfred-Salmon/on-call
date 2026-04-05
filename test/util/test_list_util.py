from src.util.list_util import get_cyclical_list_iterator, cycle_list
import pytest


def test_get_cyclical_list_iterator() -> None:
    test_list = ["a", "b", "c"]
    iterator = get_cyclical_list_iterator(test_list)

    expected = ["a", "b", "c", "a", "b", "c"]
    actual = [next(iterator) for _ in range(6)]
    assert actual == expected


def test_get_cyclical_list_iterator_empty_list() -> None:
    with pytest.raises(ValueError):
        next(get_cyclical_list_iterator([]))


def test_cycle_list() -> None:
    test_list = ["a", "b", "c"]
    assert cycle_list(test_list, -1) == ["c", "a", "b"]
    assert cycle_list(test_list, 0) == ["a", "b", "c"]
    assert cycle_list(test_list, 1) == ["b", "c", "a"]
    assert cycle_list(test_list, 2) == ["c", "a", "b"]
    assert cycle_list(test_list, 3) == ["a", "b", "c"]
    assert cycle_list(test_list, 4) == ["b", "c", "a"]


def test_cycle_list_empty_list() -> None:
    assert cycle_list([], 0) == []
    assert cycle_list([], 1) == []
    assert cycle_list([], -1) == []
