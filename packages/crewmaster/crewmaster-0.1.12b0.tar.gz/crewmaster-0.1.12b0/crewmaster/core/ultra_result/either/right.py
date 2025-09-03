from enum import Enum
from typing import TypeVar, Generic, List, Callable

T = TypeVar('T')
E = TypeVar('E')


class Variant(Enum):
    LEFT = 1
    RIGHT = 2


class Right(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value: T = value

    def get_value(self) -> T:
        return self.value

    def get_errors(self):
        raise TypeError('Cant access errors from a Right value')

    def is_left(self) -> bool:
        return False

    def is_right(self) -> bool:
        return True

    def fold(
            self, left_fn: Callable[[List[None]], T],
            right_fn: Callable[[T], T]
    ) -> T:
        return right_fn(self.get_value())


def right(value: T) -> Right[T]:
    """
    Creates a Right instance with a value.
    """
    return Right(value)
