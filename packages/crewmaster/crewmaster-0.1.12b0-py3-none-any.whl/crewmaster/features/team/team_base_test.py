import os
from typing import (
    Any,
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
    Field,
)
from langchain_openai import ChatOpenAI


from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from ..collaborator import (
    ClarificationContext,
    ClarificationMessage,
    CollaboratorInputClarification,
    CollaboratorInputFresh,
    CollaboratorOutputClarification,
    CollaboratorOutputResponse,
    CollaboratorOutputResponseStructured,
    UserMessage,
)
from ..skill import (
    BrainSchemaBase,
    ClarificationSchemaBase,
    ResultSchemaBase,
    SkillInputSchemaBase,
    ComputationRequested,
    Skill,
    SkillComputationDirect,
    SkillComputationWithClarification,
    SkillStructuredResponse,
)
from ..brain.brain_types import (
    SituationBuilderFn,
)
from ..agent.agent_base import AgentBase

from .team_base import TeamBase
from .distribution_strategy import SupervisionStrategy

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


class BalanceInput(BrainSchemaBase):
    bank: str = Field(
        ...,
        description="Name of the bank"
    )
    type: Literal[
        'checking',
        'savings'
    ] = Field(
        ...,
        description='account type'
    )


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
        value = SumOutput.parse_obj(
            {"result": number_1 + number_2}
        )
        return value


sum_computation = SumSkill()


list_items_computation: Skill = SkillStructuredResponse(
    name='list_items',
    description=(
        'shows a list of items in a structured format for the user \n'
        'use this tool when a user anwser for list of items'
    ),
    brain_schema=ListItemsInput
)


class TransferSKill(
    SkillComputationWithClarification[
        TransferBrainSchema,
        TransferClarification,
        TransferInput,
        TransferOutput
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
            **brain_input.dict(),
            **clarification_input.dict()
        }
        result = TransferInput.parse_obj(input_with_clarification)
        return result


def situation_builder(input, config):
    return 'keep focus'


tools_availables = [
    sum_computation,
    list_items_computation,
    TransferSKill(),
]


class AgentAdamSmith(AgentBase):
    name: str = 'Adam_Smith'
    job_description: str = 'Expert in Finance and Mathematics'

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
            ¿Qué quieres saber sobre matemáticas o finanzas?

    """
    options: List[Skill] = tools_availables
    situation_builder: Optional[SituationBuilderFn] = situation_builder


class AgentCervantes(AgentAdamSmith):
    name: str = 'Cervantes'
    job_description: str = 'Expert in literature'

    public_bio: str = '''
    You are a agent who work in a team trying to answer the questions
    from {user_name}.

    If the question is about Literature, you handle the answer
    using the tools at your disposition to give the most accurate answer.

    If the questions can be answered by other expert in the team
    use the tool send_message_to_colleague to ask for help.

    If you know there is another expert qualified to do the job,
    don't bother the user and send the message directly.

    If you want to send a message to another expert,
    don't ask the user, just use the tool to send the message.
    '''
    examples: str = """
    Here is an example interaction to illustrate your style:

    user: Hola, como estás?

    agent: ¡Hola {user_name}! Estoy tan bien que hasta \
            el café se pone celoso. \
            ¿Qué quieres saber sobre literatura?
    """
    options: List[Skill] = []


class AgentSupervisor(AgentBase):
    name: str = 'Pablo'
    job_description: str = '''
    Select the best team member to answer the user's question
    '''

    public_bio: str = '''
    You are a agent who work in a team trying to answer the questions
    from {user_name}.

    If the questions can be answered by other expert in the team
    use the tool send_message_to_colleague to ask for help.

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

    user: Cuánto es la raiz de 25?
    agent: send the question to Adam_Smith using the tool

    """
    options: List[Skill] = []


@pytest.fixture
def use_cases_srv():
    """Fixture para proveer el falso llm_srv"""
    result = 'aqui viene un servicio'
    # Add finalizer to reset mock after each test
    yield result


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
def config_runtime(llm_srv, use_cases_srv):
    return RunnableConfig(
        configurable={
            "llm_srv": llm_srv,
            "use_cases_srv": use_cases_srv,
            "user_name": "Pedrito",
            "today": datetime.now().isoformat(),
            "base_srv_for_transfer": use_cases_srv,
            "base_srv_for_sum": use_cases_srv,

        },
        recursion_limit=10
    )


@pytest.fixture
def team_base():
    agent_finance = AgentAdamSmith()
    agent_literature = AgentCervantes()
    agent_supervisor = AgentSupervisor()
    team = TeamBase(
        name='primer_team',
        job_description='Answer user questions',
        distribution_strategy=SupervisionStrategy(
            supervisor=agent_supervisor
        ),
        members=[
            agent_finance,
            agent_literature,
            agent_supervisor,
        ]
    )
    return team


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_what_is_my_name(team_base, config_runtime):
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='hola, cuál es mi nombre?'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await team_base.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponse)
    content = result.message.content
    assert 'Pedrito' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_sum_with_tool(team_base, config_runtime):
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=(
            'una duda de matemáticas, '
            'utilizando el tool llamado "sum", '
            'cuánto es 20 + 14?'
        )
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await team_base.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponse)
    content = result.message.content
    assert '34' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_response_structured(team_base, config_runtime):
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=(
            'Dile a AdamSmith que Quiero ver una lista de los tipos'
            ' de cuenta bancaria que existen?'
        )
    )
    input = CollaboratorInputFresh(
        message=message
    )
    result = await team_base.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponseStructured)
    structure = result.structure
    assert structure == 'list_items'


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_clarification_request(team_base, config_runtime):
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
    result = await team_base.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputClarification)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_handle_clarification_response(team_base, config_runtime):
    initial_request = UserMessage(
        id='111111',
        timestamp=datetime.now().isoformat(),
        content=(
            'Usando tool "transfer_money" Haz una transferencia de 30$  '
            ' de mi cuenta corriente a mi cuenta de ahorro'
        )
    )
    transfer_request = ComputationRequested(
        name='transfer',
        brain_args={
            "from_account": "corriente",
            "to_account": "ahorro"
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
        clarification_message=message,
        public_messages=[initial_request]
    )
    result = await team_base.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponse)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_stream_what_is_my_name(team_base, config_runtime):
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='hola, cuál es mi nombre?'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    events = []
    async for event in team_base.astream_events(
        input,
        config=config_runtime,
        version="v2",
    ):
        events.append(event)
    assert len(events) > 4
    last_event = events[-1]
    assert last_event.get('event') == 'on_chain_end'
    result = last_event.get('data', {}).get('output')
    assert isinstance(result, CollaboratorOutputResponse)
    content = result.message.content
    assert 'Pedrito' in content
