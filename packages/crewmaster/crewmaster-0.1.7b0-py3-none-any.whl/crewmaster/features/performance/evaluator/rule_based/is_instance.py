from typing import (
    Any,
    Literal,
    Optional,
    Type,
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


class IsInstanceEvaluator(RuleEvaluatorBase):
    name: Literal["is_instance"] = "is_instance"

    async def evaluate(
        self,
        input: str,
        received: Any,
        expected: Type[Any],
        alias: Optional[str] = None
    ) -> ScoreBooleanDirect:
        score = isinstance(received, expected)

        result = ScoreBooleanDirect(
            name=self.name if alias is None else alias,
            value=score
        )
        return result
