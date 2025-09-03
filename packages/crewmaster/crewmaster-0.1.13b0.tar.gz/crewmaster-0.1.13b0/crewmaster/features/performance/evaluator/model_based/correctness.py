from typing import (
    Literal,
    Optional,
)
import structlog
from langchain.evaluation.qa import (
    CotQAEvalChain,
)

from .model_evaluator_base import (
    ModelEvaluatorBase,
)

from ...score import (
    ScoreCategoricalBinary,
    ScoreError,
)


log = structlog.get_logger()
"Loger para el módulo"


class CorrectnessEvaluator(ModelEvaluatorBase):
    name: Literal["correctness"] = "correctness"

    async def evaluate(
        self,
        input: str,
        received: str,
        expected: str,
        alias: Optional[str] = None
    ) -> ScoreCategoricalBinary | ScoreError:

        evaluator = CotQAEvalChain.from_llm(llm=self.llm_judge)
        eval_result = evaluator.evaluate_strings(
            input=input,
            prediction=received,
            reference=expected,
        )
        result = ScoreCategoricalBinary(
            name=self.name if alias is None else alias,
            value=[eval_result.get('value', '')],
            explanation=eval_result.get('reasoning', ''),
            correct_categories=['CORRECT']
        )
        return result
