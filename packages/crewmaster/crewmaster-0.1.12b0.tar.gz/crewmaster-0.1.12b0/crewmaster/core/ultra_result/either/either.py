from typing import TypeVar, Union

from .right import Right
from .left import Left

T = TypeVar('T')
E = TypeVar('E')

Either = Union[Left[E], Right[T]]
