from abc import abstractmethod
from typing import (
    List,
)
from langchain_core.runnables import (
    RunnableConfig,
)

from ...core.pydantic import (
    BaseModel,
)
from ..team import (
    TeamBase,
)
from .aptitude import Aptitude
from .reporter_adapter_base import (
    ReporterAdapterBase,
)
from .perforrmance_review_result import (
    PerformanceReviewResult,
)
from .performance_review_summary import (
    PerformanceReviewSummary,
)


class PerformanceReviewBase(BaseModel):
    name: str
    agent_name: str
    team: TeamBase
    aptitudes: List[Aptitude]
    reporter: ReporterAdapterBase

    @property
    def summary(self) -> PerformanceReviewSummary:
        return PerformanceReviewSummary(
            name=self.name,
            agent_name=self.agent_name,
            aptitudes=len(self.aptitudes)
        )

    @abstractmethod
    async def execute(
        self,
        runnable_configuration: RunnableConfig
    ) -> PerformanceReviewResult:
        ...
