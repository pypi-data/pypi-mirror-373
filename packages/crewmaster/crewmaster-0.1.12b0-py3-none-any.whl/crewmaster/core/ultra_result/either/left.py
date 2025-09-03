from typing import TypeVar, Generic, List, Callable, Union

T = TypeVar('T')
E = TypeVar('E')


class Left(Generic[E]):
    def __init__(self, errors: List[E]) -> None:
        if not errors or errors is None:
            raise ValueError(
                'Errors list is null or undefined. Must pass errors list.'
            )
        if len(errors) == 0:
            raise ValueError('Errors list is empty. Must pass errors list.')
        self.errors: List[E] = errors

    def get_value(self):
        raise TypeError('Cant access value from a Left value')

    def get_errors(self) -> List[E]:
        return self.errors

    def is_left(self) -> bool:
        return True

    def is_right(self) -> bool:
        return False

    def fold(
            self, left_fn: Callable[[List[E]], T],
            right_fn: Callable[[T], T]
            ) -> T:
        return left_fn(self.get_errors())


def left(errorOrErrors: Union[E, list[E]]) -> Left[E]:
    """
    Creates a Left instance from a list of errors.
    """
    errors = errorOrErrors if isinstance(errorOrErrors, list) \
        else [errorOrErrors]
    return Left(errors)
