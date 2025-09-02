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


class PydanticModelChecker(RuleEvaluatorBase):
    name: Literal["contain"] = "contain"
    model: Type[BaseModel]

    async def evaluate(
        self,
        input: str,
        received: Any,
        expected: Any,
        alias: Optional[str] = None
    ) -> ScoreBooleanDirect:
        try:
            self.model.model_validate(received)
            return ScoreBooleanDirect(
                name=self.name if alias is None else alias,
                value=True,
            )
        except Exception as error:
            result = ScoreBooleanDirect(
                name=self.name if alias is None else alias,
                value=False,
                explanation=str(error)
            )
            return result
