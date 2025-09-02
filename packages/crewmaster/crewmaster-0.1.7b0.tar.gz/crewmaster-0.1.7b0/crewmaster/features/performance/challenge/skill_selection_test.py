import pytest
import structlog
from unittest.mock import create_autospec
from typing import (
    Type,
    List,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from langchain_core.runnables import (
    RunnableConfig,
)
from ...brain.brain_types import (
    BrainOutputComputationsRequired,
)
from ...skill import (
    BrainSchemaBase,
    ResultSchemaBase,
    ComputationRequested,
    SkillComputationDirect,
)
from ...brain.brain_base import (
    BrainBase,
)
from ..reporter_null import (
    ReporterNull,
)
from ..execution_context import (
    ExecutionContext
)
from .skill_selection import (
    SkillSelectionChallenge,
    SkillSelectionChallengePayload,
    ExpectedSkill,
)


log = structlog.get_logger()
"Loger para el módulo"


class MathInput(BrainSchemaBase):
    number_1: int
    number_2: int


class MathOutput(ResultSchemaBase):
    result: int


class SumSkill(
    SkillComputationDirect[
        MathInput,
        MathOutput
    ]
):
    name: str = 'sum'
    description: str = 'given two numbers return the sum of both'
    brain_schema: Type[MathInput] = MathInput
    result_schema: Type[MathOutput] = MathOutput

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        return []

    async def async_executor(
        self,
        request: MathInput,
        config: RunnableConfig
    ) -> MathOutput:
        value = MathOutput.model_validate(
            {"result": request.number_1 + request.number_2}
        )
        return value


class MultiplySkill(
    SkillComputationDirect[
        MathInput,
        MathOutput
    ]
):
    name: str = 'multiply'
    description: str = 'given two numbers return the multiply of both'
    brain_schema: Type[MathInput] = MathInput
    result_schema: Type[MathOutput] = MathOutput

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        return []

    async def async_executor(
        self,
        request: MathInput,
        config: RunnableConfig
    ) -> MathOutput:
        value = MathOutput.model_validate(
            {"result": request.number_1 * request.number_2}
        )
        return value


@pytest.fixture
def fake_brain():
    """Fixture para proveer el falso brain"""
    fake_brain = create_autospec(
        spec=BrainBase,
        instance=True
    )
    fake_brain.get_skills_as_dict.return_value = {
        'sum': SumSkill(),
        'multiply': MultiplySkill()
    }
    # Add finalizer to reset mock after each test
    # return fake_service
    yield fake_brain
    # Cleanup: resetear el mock para el próximo test
    fake_brain.reset_mock()


@pytest.fixture
def context(fake_brain):
    context = ExecutionContext(
        brain=fake_brain,
        reporter=ReporterNull(),
        configuration={}
    )
    return context


@pytest.mark.only
@pytest.mark.asyncio
async def test_invalid_expectations(context):
    # La expectativa no se corresponde con skills del agente
    expected_transfer = ExpectedSkill(
        name='account_transfer',
        arguments={"to": "corriente", "from": "corriente"}
    )
    data: SkillSelectionChallengePayload = SkillSelectionChallengePayload(
        expected_skills=[expected_transfer],
        message_content='Suma 14 + 29',
        user_name='Charly',
    )
    challenge = SkillSelectionChallenge(
        data=data,
        index=1,
        evaluators=[]
    )
    result = await challenge.execute(
        context
    )
    assert result.score == 0
    assert 'expected_skills' in result.fixed_aspects
    expected_skills = result.fixed_aspects['expected_skills']
    assert expected_skills.explanation == (
        'skills expected are not available in agent'
    )


@pytest.mark.only
@pytest.mark.asyncio
async def test_partial_skill_selection(context):
    # Construimos respuesta del Brain
    sum_two_numbers = ComputationRequested(
        name='sum',
        brain_args={"number_1": 10, "number_2": 20},
        computation_id='1222'
    )
    list_required = [sum_two_numbers]
    brain_output = BrainOutputComputationsRequired(
        computations_required=list_required,
        token_usage=None
    )
    context.brain.invoke.return_value = brain_output
    # Construmos el challenge
    data: SkillSelectionChallengePayload = SkillSelectionChallengePayload(
        expected_skills=[
            ExpectedSkill(name='sum', arguments={}),
            ExpectedSkill(name='multiply', arguments={})
        ],
        message_content='Dime la suma y multiplicacion de 10 + 20',
        user_name='Charly'
    )
    challenge = SkillSelectionChallenge(
        data=data,
        index=1,
        evaluators=[]
    )
    result = await challenge.execute(
        context
    )
    assert 'skills_selected' in result.fixed_aspects
    selected = result.fixed_aspects['skills_selected']
    assert selected.points == 50
    assert selected.explanation is not None
    assert "Not included: ['multiply']" in selected.explanation


@pytest.mark.only
@pytest.mark.asyncio
async def test_correct_skill_selection(context):
    sum_two_numbers = ComputationRequested(
        name='sum',
        brain_args={"number_1": 10, "number_2": 20},
        computation_id='1222'
    )
    list_required = [sum_two_numbers]
    brain_output = BrainOutputComputationsRequired(
        computations_required=list_required,
        token_usage=None
    )
    context.brain.invoke.return_value = brain_output
    # Construmos el challenge
    data: SkillSelectionChallengePayload = SkillSelectionChallengePayload(
        expected_skills=[
            ExpectedSkill(
                name='sum',
                arguments={}
            ),
        ],
        message_content='Dime la suma de 10 + 20',
        user_name='Charly'
    )
    challenge = SkillSelectionChallenge(
        data=data,
        index=1,
        evaluators=[]
    )
    result = await challenge.execute(
        context
    )
    assert 'skills_selected' in result.fixed_aspects
    selected = result.fixed_aspects['skills_selected']
    assert selected.points == 100


@pytest.mark.only
@pytest.mark.asyncio
async def test_none_correct_skill_selection(context):
    account_transfer = ComputationRequested(
        name='sum',
        brain_args={},
        computation_id='1222'
    )
    list_required = [account_transfer]
    brain_output = BrainOutputComputationsRequired(
        computations_required=list_required,
        token_usage=None
    )
    context.brain.invoke.return_value = brain_output

    data: SkillSelectionChallengePayload = SkillSelectionChallengePayload(
        expected_skills=[
            ExpectedSkill(
                name='multiply',
                arguments={}
            )
        ],
        message_content='Multiplica 10 * 10',
        user_name='Charly',
    )
    challenge = SkillSelectionChallenge(
        data=data,
        index=1,
        evaluators=[]
    )
    result = await challenge.execute(
        context
    )
    assert 'skills_selected' in result.fixed_aspects
    selected = result.fixed_aspects['skills_selected']
    assert selected.points == 0


@pytest.mark.only
@pytest.mark.asyncio
async def test_invalid_structure_for_arguments(context):
    requested_sum = ComputationRequested(
        name='sum',
        brain_args={"sumando_1": 23, "sumando_2": 70},
        computation_id='1222'
    )
    list_required = [requested_sum]
    brain_output = BrainOutputComputationsRequired(
        computations_required=list_required,
        token_usage=None
    )
    expected_transfer = ExpectedSkill(
        name='sum',
        arguments={}
    )
    context.brain.invoke.return_value = brain_output
    data: SkillSelectionChallengePayload = SkillSelectionChallengePayload(
        expected_skills=[expected_transfer],
        message_content='Suma 23 + 70',
        user_name='Charly',
    )
    challenge = SkillSelectionChallenge(
        data=data,
        index=1,
        evaluators=[]
    )
    result = await challenge.execute(
        context
    )
    assert 'skills_structure' in result.fixed_aspects
    structure = result.fixed_aspects['skills_structure']
    assert structure.points == 0
    assert structure.explanation is not None
    assert 'number_1\\n  Field required' in structure.explanation


@pytest.mark.only
@pytest.mark.asyncio
async def test_non_equal_received_to_expected(context):
    requested_sum = ComputationRequested(
        name='sum',
        brain_args={"number_1": 100, "number_2": 100},
        computation_id='1222'
    )
    list_required = [requested_sum]
    brain_output = BrainOutputComputationsRequired(
        computations_required=list_required,
        token_usage=None
    )
    expected_skill = ExpectedSkill(
        name='sum',
        arguments={"number_1": 23, "number_2": 70}
    )
    context.brain.invoke.return_value = brain_output
    data: SkillSelectionChallengePayload = SkillSelectionChallengePayload(
        expected_skills=[expected_skill],
        message_content='Suma 23 + 70',
        user_name='Charly',
    )
    challenge = SkillSelectionChallenge(
        data=data,
        index=1,
        evaluators=[]
    )
    result = await challenge.execute(
        context
    )
    assert 'skills_equality' in result.fixed_aspects
    equality = result.fixed_aspects['skills_equality']
    assert equality.points == 0
    assert equality.explanation is not None
    explanation = equality.explanation
    assert "expected: {\'number_1\': 23" in explanation
    assert "received: {\'number_1\': 100" in explanation
