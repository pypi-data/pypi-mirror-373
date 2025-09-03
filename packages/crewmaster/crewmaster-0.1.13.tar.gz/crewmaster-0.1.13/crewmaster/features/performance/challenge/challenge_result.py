from typing import (
    Dict,
)
import structlog
from ....core.pydantic import (
    BaseModel,
)
from ..score import (
    Score,
)


log = structlog.get_logger()
"Loger para el módulo"


class ChallengeResult(BaseModel):
    score: int
    fixed_aspects: Dict[str, Score]
    dynamic_aspects: Dict[str, Score] = {}
