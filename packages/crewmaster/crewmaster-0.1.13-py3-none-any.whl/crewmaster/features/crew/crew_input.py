from typing import (
    Literal,
    Union,
    Annotated,
)
from ...core.pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
)
import structlog


from ..collaborator import (
    UserMessage,
    ClarificationSimpleMessage,
)


log = structlog.get_logger()
"Loger para el módulo"


class CrewInputBase(BaseModel):
    pass


class CrewInputFresh(CrewInputBase):
    type: Literal['crew.input.fresh'] = 'crew.input.fresh'
    message: UserMessage


class CrewInputClarification(
    CrewInputBase,
):
    type: Literal['crew.input.clarification'] = 'crew.input.clarification'
    clarification_message: ClarificationSimpleMessage


CrewInput = Union[
    CrewInputFresh,
    CrewInputClarification,
]

CrewInputAdapter: TypeAdapter[CrewInput] = TypeAdapter(
    Annotated[
        CrewInput,
        Field(discriminator='type')
    ]
)
