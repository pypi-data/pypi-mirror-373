from typing import (
    Generic,
    List,
    TypeVar,
)
import structlog
from ...core.pydantic import (
    BaseModel,
)
from .challenge import (
    ChallengeBase,
)

from .aptitude_result import (
    AptitudeResult,
)
from .execution_context import (
    ExecutionContext
)
from .aptitude_summary import (
    AptitudeSummary,
)


log = structlog.get_logger()
"Loger para el módulo"


ChallengeType = TypeVar('ChallengeType', bound=ChallengeBase)


class AptitudeBase(
    BaseModel,
    Generic[ChallengeType]
):
    challenges: List[ChallengeType]
    name: str

    @property
    def summary(self) -> AptitudeSummary:
        return AptitudeSummary(
            name=self.name,
            challenges=len(self.challenges)
        )

    async def execute(
        self,
        context: ExecutionContext
    ) -> AptitudeResult:
        context.reporter.start_aptitude(self.summary)
        results = {challenge.index: await challenge.execute(
                        context=context
                    )
                   for challenge in self.challenges}
        # Extraemos los scores individuales
        scores = [result.score for result in results.values()]
        # calculamos el score del aptitude
        score = sum(scores) / len(scores) if scores else 0

        result = AptitudeResult(
            score=int(score),
            results=results
        )
        context.reporter.end_aptitude(result)
        return result
