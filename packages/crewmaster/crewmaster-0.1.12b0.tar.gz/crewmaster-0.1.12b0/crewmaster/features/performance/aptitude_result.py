from typing import (
    Dict,
)
import structlog
from ...core.pydantic import (
    BaseModel,
)
from .challenge import (
    ChallengeResult,
)

log = structlog.get_logger()
"Loger para el módulo"


class AptitudeResult(BaseModel):
    score: int
    results: Dict[int, ChallengeResult]
