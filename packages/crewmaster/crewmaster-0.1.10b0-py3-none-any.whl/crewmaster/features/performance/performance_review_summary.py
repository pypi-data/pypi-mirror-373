import structlog
from ...core.pydantic import (
    BaseModel,
)


log = structlog.get_logger()
"Loger para el módulo"


class PerformanceReviewSummary(BaseModel):
    name: str
    agent_name: str
    aptitudes: int
