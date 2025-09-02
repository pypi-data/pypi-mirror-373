
from typing import (
    Literal,
)
import structlog

from .challenge_base import (
    ChallengePayloadBase,
    ChallengeBase,
    ChallengeResult,
)
from ..execution_context import (
    ExecutionContext
)

log = structlog.get_logger()
"Loger para el módulo"


class StructuredResponseChallengePayload(ChallengePayloadBase):
    ...


class StructuredResponseChallenge(
    ChallengeBase[
        StructuredResponseChallengePayload
    ]
):
    type: Literal[
        'performance.challenge.structured_response'
    ] = 'performance.challenge.structured_response'

    def execute(
        self,
        context: ExecutionContext
    ) -> ChallengeResult:
        reporter = context.reporter
        reporter.start_challenge(self.summary)
        return ChallengeResult(
            score=100,
            fixed_aspects={},
            dynamic_aspects={}
        )
