from typing import (
    Literal,
    Optional,
)
import structlog
from deepeval.metrics import GEval
from deepeval.models import DeepEvalBaseLLM
from langchain_core.language_models import (
    BaseLanguageModel,
)
from deepeval.test_case import (
    LLMTestCase,
    LLMTestCaseParams,
)


from .model_evaluator_base import (
    ModelEvaluatorBase,
)

from ...score import (
    ScorePercentDirect,
    ScoreError,
)


log = structlog.get_logger()
"Loger para el módulo"


class OpenAIWrapper(DeepEvalBaseLLM):
    def __init__(self, llm_judge: BaseLanguageModel):
        self.llm_judge = llm_judge

    def load_model(self):
        return self.llm_judge

    def generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        return str(chat_model.invoke(prompt).content)

    async def a_generate(self, prompt: str) -> str:
        chat_model = self.load_model()
        res = await chat_model.ainvoke(prompt)
        return str(res.content)

    def get_model_name(self):
        return "Wrapper Open AI"


class CoherenceEvaluator(ModelEvaluatorBase):
    name: Literal["coherence"] = "coherence"

    async def evaluate(
        self,
        input: str,
        received: str,
        expected: str,
        alias: Optional[str] = None
    ) -> ScorePercentDirect | ScoreError:

        test_case = LLMTestCase(
            input=input,
            actual_output=received,
            expected_output=expected
        )
        model = OpenAIWrapper(llm_judge=self.llm_judge)
        metric = GEval(
            model=model,
            name="Coherence",
            criteria=("Coherence - the collective quality "
                      "of all sentences in the actual output"),
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        )
        await metric.a_measure(
            test_case=test_case,
            _show_indicator=False,
        )
        value = 0 if metric.score is None else metric.score * 100
        return ScorePercentDirect(
            name=self.name if alias is None else alias,
            explanation=metric.reason,
            value=int(value)
        )
