from abc import abstractmethod
from typing import (
    Optional,
    Annotated,
)
import structlog
from ....core.pydantic import (
    BaseModel,
    Field,
)


log = structlog.get_logger()
"Loger para el módulo"

Percent = Annotated[int, Field(ge=0, le=100)]


class ScoreBase(BaseModel):
    name: str
    explanation: Optional[str] = None

    @property
    @abstractmethod
    def points(self) -> Percent:
        ...
