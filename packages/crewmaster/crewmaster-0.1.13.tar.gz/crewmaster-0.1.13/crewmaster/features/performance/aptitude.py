from typing import (
    Annotated,
    Literal,
    Union,
    List,
    Optional,
)
import structlog
from ...core.pydantic import (
    Field,
    TypeAdapter,
)
from .aptitude_base import (
    AptitudeBase,
)
from .challenge import (
    CollaborationChallenge,
    FreeResponseChallenge,
    SkillInterpretationChallenge,
    SkillSelectionChallenge,
    StructuredResponseChallenge,
)

log = structlog.get_logger()
"Loger para el módulo"


class CollaborationAptitude(
    AptitudeBase[CollaborationChallenge]
):
    type: Literal[
        'performance.aptitude.collaboration'
    ] = 'performance.aptitude.collaboration'
    name: str = 'Collaboration'
    challenges: Optional[List[CollaborationChallenge]] = None


class SkillSelectionAptitude(
    AptitudeBase[SkillSelectionChallenge]
):
    type: Literal[
        'performance.aptitude.skill_selection'
    ] = 'performance.aptitude.skill_selection'
    name: str = 'Skill Selection'
    challenges: Optional[List[SkillSelectionChallenge]] = None


class SkillInterpretationAptitude(
    AptitudeBase[SkillInterpretationChallenge]
):
    type: Literal[
        'performance.aptitude.skill_interpretation'
    ] = 'performance.aptitude.skill_interpretation'
    name: str = 'Skill Interpretation'
    challenges: Optional[List[SkillInterpretationChallenge]] = None


class FreeResponseAptitude(
    AptitudeBase[FreeResponseChallenge]
):
    type: Literal[
        'performance.aptitude.free_response'
    ] = 'performance.aptitude.free_response'
    name: str = 'Free Response'
    challenges: Optional[List[FreeResponseChallenge]] = None


class StructuredResponseAptitude(
    AptitudeBase[StructuredResponseChallenge]
):
    type: Literal[
        'performance.aptitude.structured_response'
    ] = 'performance.aptitude.structured_response'
    name: str = 'Structured Response'
    challenges: Optional[List[StructuredResponseChallenge]] = None


Aptitude = Union[
    CollaborationAptitude,
    FreeResponseAptitude,
    SkillInterpretationAptitude,
    SkillSelectionAptitude,
    StructuredResponseAptitude,
]

AptitudeAdapter: TypeAdapter[Aptitude] = TypeAdapter(
    Annotated[
        Aptitude,
        Field(discriminator='type')
    ]
)
