from typing import (
    Any,
    Literal,
    Optional,
    Type,
)
import structlog
from .....core.pydantic import (
    BaseModel,
)
from .rule_evaluator_base import (
    RuleEvaluatorBase,
)
from ...score import (
    ScoreBooleanDirect,
)

log = structlog.get_logger()
"Loger para el módulo"


class PydanticModelEquality(RuleEvaluatorBase):
    name: Literal["pydantic_model_equality"] = "pydantic_model_equality"
    model: Type[BaseModel]

    async def evaluate(
        self,
        input: str,
        received: Any,
        expected: Any,
        alias: Optional[str] = None
    ) -> ScoreBooleanDirect:
        name = self.name if alias is None else alias
        try:
            received_model = self.model.model_validate(received)
            expected_model = self.model.model_validate(expected)
            value = received_model == expected_model
            explanation = None if value else (
                f'expected: {str(expected)}, received: {str(received)}'
            )
            return ScoreBooleanDirect(
                name=name,
                value=value,
                explanation=explanation
            )
        except Exception as error:
            result = ScoreBooleanDirect(
                name=name,
                value=False,
                explanation=str(error)
            )
            return result
