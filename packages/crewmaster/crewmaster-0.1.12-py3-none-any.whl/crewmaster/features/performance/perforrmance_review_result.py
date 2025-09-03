from typing import (
    Any,
    Dict,
)
from datetime import (
    datetime
)

from ...core.pydantic import (
    BaseModel,
)


class PerformanceReviewResult(BaseModel):
    date: datetime
    result: Dict[str, Any]
    global_score: int
    version: str
    name: str
