from typing import (
    Annotated,
    Any,
    Dict,
    Literal,
    Union,
    Generic,
)
from ...core.pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
)
import structlog

from langchain_openai import ChatOpenAI

from .message import (
    AgentMessage,
)
from .types import (
    ClarificationRequested,
    ClarificationContext,
)
from ..skill import (
    BrainSchema,
)


log = structlog.get_logger()
"Loger para el módulo"


class CollaboratorOutputBase(BaseModel):
    pass


class CollaboratorOutputClarification(
    CollaboratorOutputBase,
    Generic[
        BrainSchema
    ]
):
    type: Literal['output.clarification'] = 'output.clarification'
    clarification_context: ClarificationContext
    clarification_requested: ClarificationRequested


class CollaboratorOutputResponse(
    CollaboratorOutputBase,
):
    type: Literal['output.response'] = 'output.response'
    message: AgentMessage


class CollaboratorOutputResponseStructured(
    CollaboratorOutputBase,
):
    type: Literal['output.response_structured'] = 'output.response_structured'
    payload: Dict[str, Any]
    structure: str
    message: AgentMessage


class CollaboratorOutputContribution(
    CollaboratorOutputBase,
):
    type: Literal['output.contribution'] = 'output.contribution'
    contribution: AgentMessage


class CollaboratorConfig(BaseModel):
    llm_srv: ChatOpenAI
    use_cases_srv: Any
    user_name: str = Field(...)
    today: str


CollaboratorOutput = Union[
    CollaboratorOutputClarification[
        BrainSchema
    ],
    CollaboratorOutputResponse,
    CollaboratorOutputResponseStructured,
    CollaboratorOutputContribution,
]


CollaboratorOutputAdapter: TypeAdapter[CollaboratorOutput] = TypeAdapter(
    Annotated[
        CollaboratorOutput,
        Field(discriminator='type')
    ]
)
