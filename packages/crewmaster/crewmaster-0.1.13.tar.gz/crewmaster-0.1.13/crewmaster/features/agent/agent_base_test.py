import os
from abc import abstractmethod
from unittest.mock import create_autospec

from typing import (
    List,
    Literal,
    Optional,
    Type,
)
import pytest
import structlog
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # Carga las variables desde .env

from ...core.pydantic import (
    BaseModel,
    SecretStr,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)

from langchain_openai import ChatOpenAI


from langchain_core.runnables import (
    RunnableConfig,
)
from ..collaborator import (
    CollaboratorInputFresh,
    CollaboratorInputClarification,
    CollaboratorOutputResponse,
    CollaboratorOutputClarification,
    CollaboratorOutputResponseStructured,
    CollaboratorOutputContribution,
    TeamMembership,
    ClarificationContext,
    Colleague,
    UserMessage,
    ClarificationMessage,
)
from ..skill import (
    Skill,
    BrainSchemaBase,
    ResultSchemaBase,
    ClarificationSchemaBase,
    SkillComputationWithClarification,
    SkillComputationDirect,
    SkillStructuredResponse,
    SkillContribute,
    ComputationRequested,
)
from ..brain.brain_types import (
    InstructionsTransformerFn,
    SituationBuilderFn,
)
from .agent_base import AgentBase

log = structlog.get_logger()
"Loger para el módulo"


class SumInput(BrainSchemaBase):
    number_1: int
    number_2: int


class SumOutput(ResultSchemaBase):
    result: int


class SingleItemsInput(BaseModel):
    name: str
    description: str


class ListItemsInput(BrainSchemaBase):
    items: List[SingleItemsInput]


class TransferBrainSchema(BrainSchemaBase):
    from_account: str
    to_account: str


class TransferClarification(ClarificationSchemaBase):
    confirmation: Literal['y', 'n']


class TransferInput(BrainSchemaBase):
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


class SumSkillRepositoryPort:
    @abstractmethod
    def sumar(x, y) -> int:
        ...


class SumSkill(
    SkillComputationDirect[SumInput, SumOutput]
):
    name: str = 'sum'
    description: str = 'given two numbers return the sum of both'

    brain_schema: Type[SumInput] = SumInput
    result_schema: Type[SumOutput] = SumOutput

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        return [
            ConfigurableFieldSpec(
                id='repository_srv',
                name='Servicio requerido por el use case',
                description=(
                    'Se utiliza para inicializar el use case'
                ),
                annotation=SumSkillRepositoryPort,
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
        value = SumOutput.parse_obj(
            {"result": number_1 + number_2}
        )
        return value


list_items_computation: Skill = SkillStructuredResponse(
    name='list_items',
    description=(
        'shows a list of items in a structured format for the user \n'
        'use this tool when a user anwser for list of items'
    ),
    brain_schema=ListItemsInput
)


class TransferSkillRepositoryPort:
    @abstractmethod
    def transfer(x, y) -> int:
        ...


class TransferSkill(
    SkillComputationWithClarification[
        TransferInput,
        TransferClarification,
        TransferInput,
        TransferOutput
    ],
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
                id='repository_srv',
                name='Servicio requeridisimo por el use case',
                description=(
                    'Se utiliza para inicializar el use case'
                ),
                annotation=TransferSkillRepositoryPort,
                default=...
            )
        ]

    async def async_executor(
        self,
        request: TransferInput,
        config: RunnableConfig
    ) -> TransferOutput:
        value = TransferOutput.parse_obj(
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


def situation_builder(input, config):
    return 'keep focus'

def instructions_transformer(input, config):
    return 'super transformada'


skills_availables = [
    list_items_computation,
    SkillContribute(),
    SumSkill(),
    TransferSkill(),
]


class AgentFake(AgentBase):
    name: str = 'Adam_Smith'
    job_description: str = '''
    Answer questions only about Finance and Mathematics.
    '''

    public_bio: str = '''
    You are a agent who work in a team trying to answer the questions
    from {user_name}.

    If the question is about Finance and Mathematics, you handle the answer
    using the tools at your disposition to give the most accurate answer.

    If there is a tool to handle the request, use the tool.

    If the questions can be answered by other expert in the team
    use the tool send_message_to_colleague to ask for help.

    If you know there is another expert qualified to do the job,
    don't bother the user and send the message directly.

    If you want to send a message to another expert,
    don't ask the user, just use the tool to send the message.
    '''

    directives: str = '''


    Use three sentences maximum and keep the answer as concise as possible.

    You speak exclusively in Spanish and always maintain a friendly,
    humorous tone, sometimes with a touch of
    sarcasm to keep the conversation lively and engaging.

    Remember to always address {user_name} by their name, \
    keep the conversation light and engaging.
    '''
    examples: str = """
    Here is an example interaction to illustrate your style:

    user: Hola, como estás?

    agent: ¡Hola {user_name}! Estoy tan bien que hasta \
            el café se pone celoso. \
            ¿Qué quieres saber sobre finanzas o matemáticas?

    user: Cuál es el planeta más lejano del sol?

    agent: send the question to other colleague expert in astronomy

    """
    team_membership: Optional[TeamMembership] = TeamMembership(
        name='Fake Team',
        instructions=(
            'You are part of a team of colleagues.'
            'Please use tool if you need to send a message to anyone.\n\n'
            '"""Members:"""\n'
        ),
        members=[
            Colleague(
                name='Cervantes',
                job_description='Answer questions about Literature'
            ),
            Colleague(
                name='Sagan',
                job_description='Answer questions about Astronomy'
            ),
        ],
    )
    options: List[Skill] = skills_availables

class AgentFakeTransformer(AgentFake):
    situation_builder: Optional[SituationBuilderFn] = situation_builder
    instructions_transformer: Optional[InstructionsTransformerFn] = instructions_transformer


@pytest.fixture
def repository_incomplete_srv():
    """Fixture para proveer el falso repository_srv"""
    # Creamos una clase que tiene sólo uno de los los puertos requeridos
    # Faltaría el de transfer para estar completo
    class RepositoryPort(TransferSkillRepositoryPort):
        pass

    fake_service = create_autospec(
        spec=RepositoryPort,
        instance=True
    )
    # Add finalizer to reset mock after each test
    yield fake_service
    # Cleanup: resetear el mock para el próximo test
    fake_service.reset_mock()


@pytest.fixture
def repository_srv():
    """Fixture para proveer el falso repository_srv"""
    # Creamos una clase que tiene todos los puertos requeridos
    # por los skills en sus config_specs
    class RepositoryPort(SumSkillRepositoryPort, TransferSkillRepositoryPort):
        pass

    fake_service = create_autospec(
        spec=RepositoryPort,
        instance=True
    )
    # Add finalizer to reset mock after each test
    yield fake_service
    # Cleanup: resetear el mock para el próximo test
    fake_service.reset_mock()


@pytest.fixture
def llm_srv():
    """Fixture para proveer el falso llm_srv"""
    LLM_API_KEY_OPEN_AI = os.environ.get("LLM_API_KEY_OPEN_AI")  # noqa E501
    LLM_MODEL_OPEN_AI = os.environ.get("LLM_MODEL_OPEN_AI") or "gpt-3.5-turbo"
    # Arrange: obtener el valor que va a ser inyectado en el tests
    fake_service = ChatOpenAI(
        api_key=SecretStr(LLM_API_KEY_OPEN_AI),
        model=LLM_MODEL_OPEN_AI
    )
    # Add finalizer to reset mock after each test
    yield fake_service


@pytest.fixture
def config_runtime(llm_srv, repository_srv):
    return RunnableConfig(
        configurable={
            "llm_srv": llm_srv,
            "repository_srv": repository_srv,
            "user_name": "Pedrito",
            "today": datetime.now().isoformat(),
        },
        recursion_limit=10
    )


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_repository_incomplete(llm_srv, repository_incomplete_srv):
    config_incomplete = RunnableConfig(
        configurable={
            "llm_srv": llm_srv,
            "user_name": "Pedrito",
            "today": datetime.now().isoformat(),
            "repository_srv": repository_incomplete_srv
        },
        recursion_limit=10
    )
    agent = AgentFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='hola, sabes cuál es mi nombre?'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    with pytest.raises(ValueError) as exc_info:
        await agent.ainvoke(input, config_incomplete)
    assert 'should be an instance of RepositorySrvProtocol' in str(
        exc_info.value
    )


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_hello(config_runtime):
    agent = AgentFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='hola, sabes cuál es mi nombre?'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await agent.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponse)
    content = result.message.content
    assert 'Pedrito' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_computation_required(config_runtime):
    agent = AgentFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='utilizando el tool llamado "sum", cuánto es 20 + 14?'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await agent.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponse)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_clarification_required(config_runtime):
    agent = AgentFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=(
            'Usando tool "transfer_money" Haz una transferencia de 25$  '
            ' de mi cuenta corriente a mi cuenta de ahorro'
        )
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await agent.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputClarification)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_response_structured(config_runtime):
    agent = AgentFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=(
            'Quiero ver una lista de los tipos'
            ' de cuenta bancaria que existen?'
        )
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await agent.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponseStructured)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_contribution(config_runtime):
    agent = AgentFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=(
            'Una pregunta de literatura, '
            'quién escribió la novela 100 martirios insoportables?'
        )
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await agent.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputContribution)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_handle_clarification_response(config_runtime):
    agent = AgentFake()
    transfer_request = ComputationRequested(
        name='transfer',
        brain_args={
            "from_account": "corriente",
            "to_account": "ahorro",
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
    input = CollaboratorInputClarification(
        clarification_message=message
    )
    result = await agent.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponse)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_stream_hello(config_runtime):
    agent = AgentFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='hola, sabes cuál es mi nombre?'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    events = []
    async for event in agent.astream_events(
        input,
        config=config_runtime,
        version="v2",
    ):
        events.append(event)

    last_event = events[-1]
    assert last_event.get('event') == 'on_chain_end'
    result = last_event.get('data', {}).get('output')
    assert isinstance(result, CollaboratorOutputResponse)
    content = result.message.content
    assert 'Pedrito' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_instructions_transformer_passed_to_brain(config_runtime):
    agent = AgentFakeTransformer()
    brain = agent._brain
    instructions_transformer_fn = brain.instructions_transformer
    assert callable(instructions_transformer_fn) == True
    transformed = brain.instructions_transformer('prueba', config_runtime)
    assert transformed == 'super transformada'


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_situation_builder_passed_to_brain(config_runtime):
    agent = AgentFakeTransformer()
    brain = agent._brain
    situation_builder_fn = brain.situation_builder
    assert callable(situation_builder_fn) == True
    transformed = brain.situation_builder('prueba', config_runtime)
    assert transformed == 'keep focus'