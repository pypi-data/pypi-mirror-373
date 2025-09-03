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


class ContainEvaluator(RuleEvaluatorBase):
    name: Literal["contain"] = "contain"

    async def evaluate(
        self,
        input: str,
        received: str,
        expected: str,
        alias: Optional[str] = None
    ) -> ScoreBooleanDirect:
        score = (expected in received)
        result = ScoreBooleanDirect(
            name=self.name if alias is None else alias,
            value=score
        )
        return result
