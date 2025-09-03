from typing import (
    Annotated,
    List,
    Literal,
    Union,
)
from ...core.pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
    SerializeAsAny,
)
import structlog
from ..collaborator import (
    ClarificationRequested,
    ClarificationContext,
    ClarificationMessage,
)
from ..skill import (
    ComputationRequested,
    ComputationResult,
)

log = structlog.get_logger()
"Loger para el módulo"


class MuscleInputComputationRequested(
    BaseModel
):
    type: Literal[
        'muscle.output.computations'
    ] = 'muscle.output.computations'
    computations_required: List[ComputationRequested]


class MuscleInputClarificationResponse(
    BaseModel,
):
    type: Literal[
        'muscle.input.clarification'
    ] = 'muscle.input.clarification'
    clarification_message: ClarificationMessage


MuscleInput = Union[
    MuscleInputComputationRequested,
    MuscleInputClarificationResponse
]

"""Union discriminada para MuscleInput"""
MuscleInputAdapter: TypeAdapter[MuscleInput] = TypeAdapter(
    Annotated[
        MuscleInput,
        Field(discriminator='type')
    ]
)


class MuscleOutputClarification(
    BaseModel,
):
    type: Literal[
        'muscle.output.clarification'
    ] = 'muscle.output.clarification'
    clarification_context: ClarificationContext
    clarification_requested: SerializeAsAny[ClarificationRequested]


class MuscleOutputResults(
    BaseModel,
):
    type: Literal['muscle.output.results'] = 'muscle.output.results'
    computations_requested: List[ComputationRequested] = []
    computations_results: List[ComputationResult] = []


MuscleOutput = Union[
    MuscleOutputClarification,
    MuscleOutputResults
]

"""Union discriminada para MuscleOutput"""
MuscleOutputAdapter: TypeAdapter[MuscleOutput] = TypeAdapter(
    Annotated[
        MuscleOutput,
        Field(discriminator='type')
    ]
)
