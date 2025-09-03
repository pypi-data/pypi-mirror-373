from typing import Literal
from ..evaluator_base import (
    EvaluatorBase
)
from langchain_core.language_models import (
    BaseLanguageModel,
)


class ModelEvaluatorBase(EvaluatorBase):
    llm_judge: BaseLanguageModel
    evaluator: Literal['model_based'] = 'model_based'
