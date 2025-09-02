from abc import abstractmethod
from typing import Optional
import structlog
from ....core.pydantic import (
    BaseModel,
)
from ..score import (
    Score,
)

log = structlog.get_logger()
"Loger para el módulo"


class EvaluatorBase(BaseModel):
    name: str

    @abstractmethod
    async def evaluate(
        self,
        input: str,
        received: str,
        expected: str,
        alias: Optional[str] = None
    ) -> Score:
        ...
