import structlog
from ...core.pydantic import (
    BaseModel,
)


log = structlog.get_logger()
"Loger para el módulo"


class AptitudeSummary(BaseModel):
    name: str
    challenges: int
