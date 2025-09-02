from abc import (
    ABC, abstractmethod
)
from pydantic import (
    BaseModel as BaseModelV2
)
from .user_logged import (
    UserLogged
)


class AuthStrategyInterface(ABC, BaseModelV2):
    @abstractmethod
    def execute(
        self
    ) -> UserLogged:
        pass

    @abstractmethod
    def current_user(
        self
    ) -> UserLogged:
        pass
