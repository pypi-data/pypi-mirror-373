from abc import abstractmethod

import structlog
from ...core.pydantic import (
    BaseModel,
)
from .perforrmance_review_result import (
    PerformanceReviewResult,
)
from .performance_review_summary import (
    PerformanceReviewSummary,
)
from .aptitude_result import (
    AptitudeResult,
)
from .aptitude_summary import (
    AptitudeSummary,
)
from .challenge import (
    ChallengeResult,
    ChallengeSummary,
)


log = structlog.get_logger()
"Loger para el módulo"


class ReporterAdapterBase(BaseModel):

    @abstractmethod
    def start_performance(
        self,
        summary: PerformanceReviewSummary
    ) -> None:
        ...

    @abstractmethod
    def start_aptitude(
        self,
        summary: AptitudeSummary
    ) -> None:
        ...

    @abstractmethod
    def start_challenge(
        self,
        summary: ChallengeSummary
    ) -> None:
        ...

    @abstractmethod
    def end_challenge(
        self,
        result: ChallengeResult
    ) -> None:
        ...

    @abstractmethod
    def end_aptitude(
        self,
        result: AptitudeResult
    ) -> None:
        ...

    @abstractmethod
    def end_performance(
        self,
        result: PerformanceReviewResult
    ) -> None:
        ...
