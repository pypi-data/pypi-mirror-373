from typing import (
    Any,
    List,
    Literal,
    Type,
)
import pytest
import structlog
from datetime import datetime

from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)

from langchain_core.runnables import (
    RunnableConfig,
)
from langserve.serialization import WellKnownLCSerializer
from ..collaborator import (
    ClarificationMessage,
    ClarificationContext,
    UserMessage,
)
from ..skill import (
    Skill,
    SkillComputationDirect,
    SkillComputationWithClarification,
    ComputationRequested,
    BrainSchemaBase,
    ResultSchemaBase,
    ClarificationSchemaBase,
    SkillInputSchemaBase,
)
from .muscle_types import (
    MuscleInputClarificationResponse,
    MuscleInputComputationRequested,
    MuscleOutputClarification,
    MuscleOutputResults,
)
from .muscle_base import (
    MuscleBase
)

log = structlog.get_logger()
"Loger para el módulo"


class SumInput(BrainSchemaBase):
    number_1: int
    number_2: int


class SumOutput(ResultSchemaBase):
    result: int


class TransferBrainSchema(BrainSchemaBase):
    from_account: str
    to_account: str


class TransferClarification(ClarificationSchemaBase):
    confirmation: Literal['y', 'n']


class TransferInput(SkillInputSchemaBase):
    from_account: str
    to_account: str
    confirmation: Literal['y', 'n']


class TransferOutput(ResultSchemaBase):
    result: str
    new_balance: int


def create_message(content: str):
    return UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=content
    )


class SumSkill(
    SkillComputationDirect[
        SumInput,
        SumOutput
    ]
):
    name: str = 'sum'
    description: str = 'given two numbers return the sum of both'

    brain_schema: Type[SumInput] = SumInput
    result_schema: Type[SumOutput] = SumOutput

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        return [
            ConfigurableFieldSpec(
                id='base_srv_for_sum',
                name='Servicio requerido por el use case',
                description=(
                    'Se utiliza para inicializar el use case'
                ),
                annotation=Any,
                default=...
            )
        ]

    async def async_executor(
        self,
        request: SumInput,
        config: RunnableConfig
    ) -> SumOutput:
        number_1 = request.number_1
        number_2 = request.number_2
        value = SumOutput.model_validate(
            {"result": number_1 + number_2}
        )
        return value


sum_computation = SumSkill()


class TransferSKill(
    SkillComputationWithClarification[
        TransferBrainSchema,
        TransferClarification,
        TransferInput,
        TransferOutput,
    ]
):
    name: str = 'transfer'
    description: str = 'transfer money between accounts'
    brain_schema: Type[TransferBrainSchema] = TransferBrainSchema
    result_schema: Type[TransferOutput] = TransferOutput
    skill_input_schema: Type[TransferInput] = TransferInput
    clarification_schema: Type[TransferClarification] = TransferClarification

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        """List configurable fields for this runnable."""
        return [
            ConfigurableFieldSpec(
                id='base_srv_for_transfer',
                name='Servicio requeridisimo por el use case',
                description=(
                    'Se utiliza para inicializar el use case'
                ),
                annotation=Any,
                default=...
            )
        ]

    async def async_executor(
        self,
        request: TransferInput,
        config: RunnableConfig
    ) -> TransferOutput:
        value = TransferOutput.model_validate(
            {"result": "success", "new_balance": 100}
        )
        return value

    def merge_brain_with_clarification(
        self,
        brain_input: TransferBrainSchema,
        clarification_input: TransferClarification
    ) -> TransferInput:
        input_with_clarification = {
            **brain_input.model_dump(),
            **clarification_input.model_dump()
        }
        result = TransferInput.model_validate(input_with_clarification)
        return result


class MuscleFake(MuscleBase):
    agent_name: str = 'Adam_Smith'
    options: List[Skill] = [
        SumSkill(),
        TransferSKill(),
    ]


@pytest.fixture
def base_use_case_srv():
    """Fixture para proveer un falso servicio de base para los use cases"""
    result = 'aqui viene un servicio'
    # Add finalizer to reset mock after each test
    yield result


@pytest.fixture
def config_runtime(base_use_case_srv):
    config = RunnableConfig(
        configurable={
            "base_srv_for_transfer": base_use_case_srv,
            "base_srv_for_sum": base_use_case_srv,
        }
    )
    # Add finalizer to reset mock after each test
    yield config


# @pytest.mark.only
@pytest.mark.asyncio
async def test_empty_computations(config_runtime):
    brain = MuscleFake()
    input = MuscleInputComputationRequested(
        computations_required=[]
    )
    result = await brain.ainvoke(input, config_runtime)
    assert isinstance(result, MuscleOutputResults)


# @pytest.mark.only
@pytest.mark.asyncio
async def test_one_computation_with_clarification(config_runtime):
    brain = MuscleFake()
    transfer_computation = ComputationRequested(
        name='transfer',
        brain_args={
            "from_account": "ahorros-12",
            "to_account": "corrient-44"
        },
        computation_id='122222'
    )
    input = MuscleInputComputationRequested(
        computations_required=[transfer_computation]
    )
    result = await brain.ainvoke(input, config_runtime)
    assert isinstance(result, MuscleOutputClarification)


# @pytest.mark.only
@pytest.mark.asyncio
async def test_one_computation_direct(config_runtime):
    brain = MuscleFake()
    sum_request = ComputationRequested(
        name='sum',
        brain_args={
            "number_1": 10,
            "number_2": 13
        },
        computation_id='122222'
    )
    input = MuscleInputComputationRequested(
        computations_required=[sum_request]
    )
    result = await brain.ainvoke(input, config_runtime)
    assert isinstance(result, MuscleOutputResults)
    results_list = result.computations_results
    assert len(results_list) == 1
    computation = results_list[0]
    assert computation.result.result == 23


# @pytest.mark.only
@pytest.mark.asyncio
async def test_one_clarification_response(config_runtime):
    brain = MuscleFake()
    transfer_request = ComputationRequested(
        name='transfer',
        brain_args={
            "from_account": "ahorros-334",
            "to_account": "corriente-44"
        },
        computation_id='122222'
    )
    context = ClarificationContext(
        computations_requested=[transfer_request],
        computations_results=[],
        requested_by="Adam_Smith"
    )
    message = ClarificationMessage(
        to='Adam_Smith',
        payload={"confirmation": "y"},
        clarification_context=context,
        timestamp=datetime.now().isoformat(),
        computation_id='122222',
        content=''
    )
    input = MuscleInputClarificationResponse(
        clarification_message=message
    )
    result = await brain.ainvoke(input, config_runtime)
    assert isinstance(result, MuscleOutputResults)
    results_list = result.computations_results
    assert len(results_list) == 1


# @pytest.mark.only
@pytest.mark.asyncio
async def test_one_clarification_response_with_other_computation(
    config_runtime
):
    brain = MuscleFake()
    transfer_request = ComputationRequested(
        name='transfer',
        brain_args={
            "from_account": "ahorros-334",
            "to_account": "corriente-44"
        },
        computation_id='122222'
    )
    sum_computation = ComputationRequested(
        name='sum',
        brain_args={
            "number_1": 12,
            "number_2": 13
        },
        computation_id='9999999'
    )
    context = ClarificationContext(
        computations_requested=[transfer_request, sum_computation],
        computations_results=[],
        requested_by="Adam_Smith"
    )
    message = ClarificationMessage(
        to='Adam_Smith',
        payload={"confirmation": "y"},
        clarification_context=context,
        timestamp=datetime.now().isoformat(),
        computation_id='122222',
        content=''
    )
    input = MuscleInputClarificationResponse(
        clarification_message=message
    )
    result = await brain.ainvoke(input, config_runtime)
    assert isinstance(result, MuscleOutputResults)
    results_list = result.computations_results
    assert len(results_list) == 2


# @pytest.mark.only
@pytest.mark.asyncio
async def test_one_clarification_response_with_other_clarification(
    config_runtime
):
    brain = MuscleFake()
    transfer_request = ComputationRequested(
        name='transfer',
        brain_args={
            "from_account": "ahorros-334",
            "to_account": "corriente-44"
        },
        computation_id='122222'
    )
    transfer_request_2 = ComputationRequested(
        name='transfer',
        brain_args={
            "from_account": "ahorros-334",
            "to_account": "corriente-44"
        },
        computation_id='999'
    )
    context = ClarificationContext(
        computations_requested=[transfer_request, transfer_request_2],
        computations_results=[],
        requested_by="Adam_Smith"
    )
    message = ClarificationMessage(
        to='Adam_Smith',
        payload={"confirmation": "y"},
        clarification_context=context,
        timestamp=datetime.now().isoformat(),
        computation_id='122222',
        content=''
    )
    input = MuscleInputClarificationResponse(
        clarification_message=message
    )
    result = await brain.ainvoke(input, config_runtime)
    assert isinstance(result, MuscleOutputClarification)
    context = result.clarification_context
    pending = context.computations_requested
    results = context.computations_results
    requested_by = context.requested_by
    assert len(results) == 1
    assert len(pending) == 1
    assert requested_by == 'Adam_Smith'


# @pytest.mark.only
@pytest.mark.asyncio
async def test_stream_one_computation_direct(config_runtime):
    brain = MuscleFake()
    sum_request = ComputationRequested(
        name='sum',
        brain_args={
            "number_1": 10,
            "number_2": 13
        },
        computation_id='122222'
    )
    input = MuscleInputComputationRequested(
        computations_required=[sum_request]
    )
    serializer = WellKnownLCSerializer()
    events = []
    async for event in brain.astream_events(
        input,
        config=config_runtime,
        version="v2",
    ):
        # Verificamos que se pueda serializar correctamente
        serializer.dumpd(event)
        events.append(event)
    assert len(events) == 4
    last_event = events[-1]
    assert last_event.get('event') == 'on_chain_end'
    result = last_event.get('data', {}).get('output')
    assert isinstance(result, MuscleOutputResults)
    results_list = result.computations_results
    assert len(results_list) == 1
    computation = results_list[0]
    assert computation.result.result == 23
