from abc import ABC, abstractmethod
from typing import List

from ...core.pydantic import (
    BaseModel
)

from .message import AnyMessage


class HistoryStrategyInterface(BaseModel, ABC):
    @abstractmethod
    def execute(
        self,
        messages: List[AnyMessage]
    ) -> List[AnyMessage]:
        pass


class MaxMessagesStrategy(
    HistoryStrategyInterface
):
    max_number: int = 10

    def execute(
        self,
        messages: List[AnyMessage]
    ) -> List[AnyMessage]:
        return messages[-self.max_number:]
