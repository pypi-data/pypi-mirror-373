from typing import (
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Union,
    Annotated,
)
from ...core.pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
)
from langchain_core.runnables import (
    RunnableConfig,
)
import structlog

from ..collaborator import (
    AgentMessage,
    AnyMessage,
    TokenUsage
)
from ..skill import (
    ComputationRequested,
    ComputationResult,
)

log = structlog.get_logger()
"Loger para el módulo"


class BrainInputBase(BaseModel):
    messages: List[AnyMessage]
    user_name: str
    today: str


class BrainInputFresh(BrainInputBase):
    type: Literal['brain.input.fresh'] = 'brain.input.fresh'


class BrainInputResults(BrainInputBase):
    type: Literal['brain.input.clarification'] = 'brain.input.clarification'
    computations_requested: List[ComputationRequested] = []
    computations_results: List[ComputationResult] = []


BrainInput = Union[
    BrainInputFresh,
    BrainInputResults,
]

BrainInputAdapter: TypeAdapter[BrainInput] = TypeAdapter(
    Annotated[
        BrainInput,
        Field(discriminator='type')
    ]
)


class BrainOutputBase(BaseModel):
    token_usage: Optional[TokenUsage]


class BrainOutputResponse(
    BrainOutputBase,
):
    type: Literal['brain.output.response'] = 'brain.output.response'
    message: AgentMessage


class BrainOutputResponseStructured(
    BrainOutputBase,
):
    type: Literal['brain.output.structured'] = 'brain.output.structured'
    message_id: str
    payload: Dict[str, Any]
    structure: str


class BrainOutputContribution(
    BrainOutputBase,
):
    type: Literal['brain.output.contribution'] = 'brain.output.contribution'
    message: AgentMessage


class BrainOutputComputationsRequired(
    BrainOutputBase,
):
    type: Literal['brain.output.computations'] = 'brain.output.computations'
    computations_required: List[ComputationRequested]


BrainOutput = Union[
    BrainOutputComputationsRequired,
    BrainOutputContribution,
    BrainOutputResponse,
    BrainOutputResponseStructured,
]

BrainOutputAdapter: TypeAdapter[BrainOutput] = TypeAdapter(
    Annotated[
        BrainOutput,
        Field(discriminator='type')
    ]
)

SituationBuilderFn = Callable[
    [BrainInputBase, RunnableConfig],
    str
]

InstructionsTransformerFn = Callable[
    [str, BrainInputBase, RunnableConfig],
    str
]
