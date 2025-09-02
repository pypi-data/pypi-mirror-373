from abc import ABC, abstractmethod
from typing import TypeVar, Generic

# Define generic type variables
IRequest = TypeVar('IRequest')


class UseCaseBase(ABC, Generic[IRequest]):
    """
    Abstract base class for use cases.

    All use cases must implement this interface.

    Only one method is offered to "execute" the use case.
    """

    @abstractmethod
    async def execute(self, request: IRequest) -> None:
        pass
