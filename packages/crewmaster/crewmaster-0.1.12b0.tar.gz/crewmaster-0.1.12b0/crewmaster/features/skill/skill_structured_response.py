from typing import (
    Literal,
)
import structlog

from .skill_base import (
    SkillBase,
)


log = structlog.get_logger()
"Loger para el módulo"


class SkillStructuredResponse(
    SkillBase,
):
    type: Literal['skill.response_structured'] = 'skill.response_structured'
