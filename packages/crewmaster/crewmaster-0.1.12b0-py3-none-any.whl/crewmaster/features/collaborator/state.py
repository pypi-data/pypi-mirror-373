from typing import (
    List,
    Optional,
    Annotated,
)
import operator
from ...core.pydantic import (
    BaseModel,
)

import structlog

from .message import (
    PublicMessage,
    AgentMessage,
    FreshMessage,
)
from .types import (
    ComputationResult,
    ComputationRequested
)
from .collaborator_ouput import (
    CollaboratorOutput
)


log = structlog.get_logger()
"Loger para el módulo"


class CollaboratorState(BaseModel):
    public_messages: Annotated[
        List[PublicMessage],
        operator.add
    ] = []
    private_messages: Annotated[
        List[AgentMessage],
        operator.add
    ] = []
    fresh_message: FreshMessage

    output: Optional[CollaboratorOutput] = None

    computations_requested: List[ComputationRequested] = []
    computations_results: List[ComputationResult] = []
    next_step: str = ''
