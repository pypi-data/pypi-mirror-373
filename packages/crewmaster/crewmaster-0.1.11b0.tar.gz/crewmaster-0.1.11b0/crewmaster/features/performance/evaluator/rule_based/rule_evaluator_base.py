from typing import Literal
from ..evaluator_base import (
    EvaluatorBase
)


class RuleEvaluatorBase(EvaluatorBase):
    evaluator: Literal['rule_based'] = 'rule_based'
