from typing import TypeVar, Generator

T = TypeVar("T")


def get_cyclical_list_iterator(list: list[T]) -> Generator[T]:
    size = len(list)
    index = 0
    while True:
        yield list[index % size]
        index += 1
