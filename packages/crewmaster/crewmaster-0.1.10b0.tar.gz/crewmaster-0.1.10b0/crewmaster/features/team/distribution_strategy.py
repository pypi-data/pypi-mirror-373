from abc import ABC, abstractmethod
from typing import List

from ...core.pydantic import (
    BaseModel
)

import random


from ..agent.agent_base import AgentBase


class DistributionStrategyInterface(BaseModel, ABC):
    @abstractmethod
    def execute(
        self,
    ) -> AgentBase:
        pass


class RandomStrategy(
    DistributionStrategyInterface
):
    members: List[AgentBase]

    def execute(
        self,
    ) -> AgentBase:
        return random.choice(self.members)


class SupervisionStrategy(
    DistributionStrategyInterface,
):
    supervisor: AgentBase

    def execute(
        self,
    ) -> AgentBase:
        return self.supervisor
