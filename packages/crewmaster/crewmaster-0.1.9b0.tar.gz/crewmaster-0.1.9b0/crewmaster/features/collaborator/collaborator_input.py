from typing import (
    Annotated,
    List,
    Literal,
    Union,
)
from ...core.pydantic import (
    BaseModel,
    TypeAdapter,
    Field,
)
import structlog


from .message import (
    PublicMessage,
    AgentMessage,
    UserMessage,
    ClarificationMessage,
)


log = structlog.get_logger()
"Loger para el módulo"


class CollaboratorInputBase(BaseModel):
    public_messages: List[PublicMessage] = []
    private_messages: List[AgentMessage] = []


class CollaboratorInputFresh(CollaboratorInputBase):
    type: Literal['input.fresh'] = 'input.fresh'
    message: UserMessage


class CollaboratorInputClarification(
    CollaboratorInputBase
):
    type: Literal['input.clarification'] = 'input.clarification'
    clarification_message: ClarificationMessage


CollaboratorInput = Union[
    CollaboratorInputFresh,
    CollaboratorInputClarification,
]

CollaboratorInputAdapter: TypeAdapter[CollaboratorInput] = TypeAdapter(
    Annotated[
        CollaboratorInput,
        Field(discriminator='type')
    ]
)
