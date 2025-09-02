
from typing import (
    Annotated,
    Union,
)
from ....core.pydantic import (
    Field,
    TypeAdapter,
)
import structlog

from .collaboration import (
    CollaborationChallenge,
)
from .skill_interpretation import (
    SkillInterpretationChallenge,
)
from .skill_selection import (
    SkillSelectionChallenge,
)
from .free_response import (
    FreeResponseChallenge,
)
from .structured_response import (
    StructuredResponseChallenge,
)

log = structlog.get_logger()
"Loger para el módulo"


Challenge = Union[
    CollaborationChallenge,
    SkillInterpretationChallenge,
    SkillSelectionChallenge,
    FreeResponseChallenge,
    StructuredResponseChallenge,
]

ChallengeAdapter: TypeAdapter[Challenge] = TypeAdapter(
    Annotated[
        Challenge,
        Field(discriminator='type')
    ]
)
