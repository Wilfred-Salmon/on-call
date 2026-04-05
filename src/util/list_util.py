from typing import TypeVar, Generator

T = TypeVar("T")


def get_cyclical_list_iterator(list: list[T]) -> Generator[T]:
    size = len(list)
    if size == 0:
        raise ValueError("Cannot create cyclical iterator for empty list")

    index = 0
    while True:
        yield list[index % size]
        index += 1


def cycle_list(list: list[T], cycle: int) -> list[T]:
    if len(list) == 0:
        return []
    size = len(list)
    return [list[(i + cycle) % size] for i in range(size)]
