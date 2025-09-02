import structlog

from .reporter_adapter_base import (
    ReporterAdapterBase,
    AptitudeSummary,
    ChallengeSummary,
    PerformanceReviewSummary,
)

from .challenge import (
    ChallengeResult
)
from .perforrmance_review_result import (
    PerformanceReviewResult
)
from .aptitude_base import AptitudeResult

log = structlog.get_logger()
"Loger para el módulo"


class ReporterNull(ReporterAdapterBase):

    def start_performance(self, summary: PerformanceReviewSummary) -> None:
        ...

    def start_aptitude(self, summary: AptitudeSummary) -> None:
        ...

    def start_challenge(self, summary: ChallengeSummary) -> None:
        ...

    def end_challenge(self, result: ChallengeResult) -> None:
        ...

    def end_aptitude(self, result: AptitudeResult) -> None:
        ...

    def end_performance(self, result: PerformanceReviewResult) -> None:
        ...
