from typing import TypeVar

T = TypeVar('T')

def get_at_index_with_wrap(
    list: list[T],
    index: int
) -> T:
    return list[index % len(list)]
