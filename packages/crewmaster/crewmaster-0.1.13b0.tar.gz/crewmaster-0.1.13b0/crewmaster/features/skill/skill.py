from typing import (
    Annotated,
    Union,
)
from ...core.pydantic import (
    Field,
    TypeAdapter,
)
import structlog


from .skill_computation import (
    SkillComputation,
)
from .skill_contribute import (
    SkillContribute,
)
from .skill_structured_response import (
    SkillStructuredResponse
)


log = structlog.get_logger()
"Loger para el módulo"


Skill = Union[
    SkillComputation,
    SkillContribute,
    SkillStructuredResponse
]

"""Union discriminada para Skill"""
SkillAdapter: TypeAdapter[Skill] = TypeAdapter(
    Annotated[
        Skill,
        Field(discriminator='type')
    ]
)
