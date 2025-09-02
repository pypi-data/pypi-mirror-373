from uuid import uuid4
from datetime import datetime

from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Literal,
    Union,
)

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)

from ...core.pydantic import (
    BaseModel,
    Field,
)

from .types import (
    ClarificationContext,
)


class Timed(BaseModel):
    timestamp: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "timestamp": self.timestamp
        }


class WithRecipient(BaseModel):
    to: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "to": self.to
        }


class WithAuthor(BaseModel):
    author: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "author": self.author
        }


class UserMessage(HumanMessage, Timed):
    subtype: Literal['user_message'] = 'user_message'
    name: str = 'UserMessage'

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "subtype": self.subtype,
            "name": self.name
        }


class ClarificationSimpleMessage(HumanMessage, Timed):
    subtype: Literal['clarification_message'] = 'clarification_message'
    name: str = 'ClarificationSimpleMessage'
    content: Union[str, List[Union[str, Dict]]] = ''
    payload: Dict[str, Any]
    computation_id: str


class ClarificationMessage(ClarificationSimpleMessage, WithRecipient):
    name: str = 'ClarificationMessage'
    clarification_context: ClarificationContext


FreshMessage = Annotated[
    Union[UserMessage, ClarificationMessage],
    Field(discriminator='subtype')
]


class AgentMessage(
    AIMessage,
    Timed,
    WithRecipient,
    WithAuthor,
):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    timestamp: str = Field(
        default_factory=datetime.now().isoformat
    )

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp
        }


class ToolTimedMessage(ToolMessage, Timed):
    timestamp: str = Field(
        default_factory=datetime.now().isoformat
    )
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp
        }


PublicMessage = Union[
    UserMessage,
    AgentMessage,
]

PrivateMessage = Union[
    AgentMessage,
    ToolMessage
]

AnyMessage = Union[
    ClarificationMessage,
    UserMessage,
    AgentMessage,
    ToolMessage
]
