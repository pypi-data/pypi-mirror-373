from typing import (
    Annotated,
    List,
    Optional,
)
import operator
from ...core.pydantic import (
    BaseModel,
)
from ..collaborator import (
    PublicMessage,
)
from .crew_input import (
    CrewInput,
)
from .crew_output import (
    CrewOutput,
)
from .types import (
    ClarificationPending,
)


class CrewState(
    BaseModel
):
    public_messages: Annotated[
        List[PublicMessage],
        operator.add
    ] = []
    clarification: Optional[
        ClarificationPending
    ] = None
    input: CrewInput
    output: Optional[CrewOutput] = None
