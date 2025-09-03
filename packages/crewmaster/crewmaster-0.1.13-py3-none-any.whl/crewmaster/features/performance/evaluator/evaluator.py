from typing import (
    Union,
    Annotated,
)
import structlog
from ....core.pydantic import (
    TypeAdapter,
    Field,
)
from .rule_based import (
    MatchEvaluator,
    ContainEvaluator
)
from .model_based import (
    CorrectnessEvaluator,
    ToxicityEvaluator,
    CoherenceEvaluator,
)

log = structlog.get_logger()
"Loger para el módulo"


Evaluator = Union[
    MatchEvaluator,
    ContainEvaluator,
    CorrectnessEvaluator,
    ToxicityEvaluator,
    CoherenceEvaluator,
]


EvaluatorAdapter: TypeAdapter[Evaluator] = TypeAdapter(
    Annotated[
        Evaluator,
        Field(discriminator='name')
    ]
)
