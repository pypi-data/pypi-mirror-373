from typing import (
    List,
    Literal,
    Optional,
)
import structlog
from .rule_evaluator_base import (
    RuleEvaluatorBase,
)
from ...score import (
    ScorePercentDirect,
)

log = structlog.get_logger()
"Loger para el módulo"


class SubSetEvaluator(RuleEvaluatorBase):
    name: Literal["sub_set"] = "sub_set"

    async def evaluate(
        self,
        input: str,
        received: List[str],
        expected: List[str],
        alias: Optional[str] = None,
    ) -> ScorePercentDirect:
        # Ensure the `expected` list is not empty to avoid division by zero
        name = self.name if alias is None else alias
        if not expected or len(expected) == 0:
            return ScorePercentDirect(
                value=0,
                explanation='expected list is empty',
                name=name
            )
        # Calculate points per correct match
        each_success = 100 / len(expected)
        score = 0
        not_included = []
        # Iterate over expected elements and check if they are in received
        for item in expected:
            if item in received:
                score += each_success
            else:
                not_included.append(item)
        # Cap the score at 100 to handle edge cases
        value = int(min(score, 100))
        explanation = None if value == 100 else f'Not included: {not_included}'
        return ScorePercentDirect(
            value=value,
            name=name,
            explanation=explanation
        )
