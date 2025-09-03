from typing import (
    List,
)
from ...core.pydantic import (
    BaseModel,
    Field,
)
from .types import Colleague
from ..skill import Skill
import structlog


log = structlog.get_logger()
"Loger para el módulo"


class TeamMembership(BaseModel):
    name: str
    members: List[Colleague] = Field(...)
    instructions: str
    collaboration_tools: List[Skill] = []
