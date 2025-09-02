from ....core.pydantic import (
    BaseModel,
)


class ChallengeSummary(BaseModel):
    idx: int
    description: str
