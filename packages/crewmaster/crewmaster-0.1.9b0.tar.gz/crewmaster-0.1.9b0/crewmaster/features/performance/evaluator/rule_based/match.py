from typing import (
    Literal,
    Optional,
)
import structlog
from .rule_evaluator_base import (
    RuleEvaluatorBase,
)
from ...score import (
    ScoreBooleanDirect,
)

log = structlog.get_logger()
"Loger para el módulo"


class MatchEvaluator(RuleEvaluatorBase):
    name: Literal["match"] = "match"

    async def evaluate(
        self,
        input: str,
        received: str,
        expected: str,
        alias: Optional[str] = None,
    ) -> ScoreBooleanDirect:
        score = (received == expected)
        result = ScoreBooleanDirect(
            name=self.name if alias is None else alias,
            value=score
        )
        return result
