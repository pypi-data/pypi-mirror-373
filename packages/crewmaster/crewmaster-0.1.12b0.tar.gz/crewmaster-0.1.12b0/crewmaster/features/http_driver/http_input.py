from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Literal,
    Set,
    Union,
)
from pydantic import (
    BaseModel,
    Field,
)
import structlog
from .stream_conversor import (
    AllowedEventMoment,
    ScopeAvailables,
    EventFormat,
)

log = structlog.get_logger()
"Loger para el módulo"


class UserMessage(BaseModel):
    type: Literal["human"] = "human"
    subtype: Literal['user_message'] = 'user_message'
    timestamp: str
    content: Union[str, List[Union[str, Dict]]]
    id: str


class ClarificationSimpleMessage(BaseModel):
    """
    Response to a clarification message sent by the Crew.
    """
    subtype: Literal['clarification_message'] = 'clarification_message'
    content: Union[str, List[Union[str, Dict]]] = ''
    payload: Dict[str, Any]
    computation_id: str
    timestamp: str


class HttpInputFresh(BaseModel):
    """
    New input originated by a user message.

    Is the most used message in a normal conversation.

    """
    type: Literal['http.input.fresh'] = 'http.input.fresh'
    message: UserMessage


class HttpInputClarification(BaseModel):
    type: Literal['http.input.clarification'] = 'http.input.clarification'
    clarification_message: ClarificationSimpleMessage


HttpInput = Annotated[
    Union[HttpInputClarification, HttpInputFresh],
    Field(..., discriminator='type')
]


class HttpMetadata(BaseModel):
    thread_id: str


class HttpEventFilter(BaseModel):
    """
    Define the type, time and format of the messages in the stream.

    The defaults allows to receive the less amount of message,
    with the smallest size.
    """
    scope: ScopeAvailables = Field(
        'answer',
        description="""
    Type of events that will be sent in the stream.

    * answer: Only the definitive answer will be sent
    * deliberations: Messages between agents
    * computations: connections with others systems and skills

    Each level include the previous events.
    """
    )
    """
    Type of events that will be sent in the stream.

    * answer: Only the definitive answer will be sent
    * deliberations: Messages between agents
    * computations: connections with others systems and skills

    Each level include the previous events.
    """
    moments: Set[AllowedEventMoment] = Field(
        {"end"},
        description="""
    Time of the event that will be sent.
    * start: the start of every process
    * stream: the intermediate events in the agent
    * end: the final of the process
    """)
    format: EventFormat = Field(
        'compact',
        description="""
    Use compact to receive only the event data.
    Use extended to also receive the event metadata.
    """)
