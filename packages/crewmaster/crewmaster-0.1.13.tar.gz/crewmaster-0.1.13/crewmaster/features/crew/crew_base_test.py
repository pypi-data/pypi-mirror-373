import os
from typing import (
    Any,
    Dict,
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
from langchain_core.load.serializable import Serializable
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import (
    MemorySaver,
)

from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from langchain_core.runnables import (
    RunnableConfig,
)
from ..collaborator import (
    CollaboratorOutputClarification,
    CollaboratorOutputResponse,
    CollaboratorOutputResponseStructured,
    UserMessage,
    ClarificationSimpleMessage,
)
from ..skill import (
    BrainSchemaBase,
    ClarificationSchemaBase,
    ResultSchemaBase,
    Skill,
    SkillComputationDirect,
    SkillComputationWithClarification,
    SkillInputSchemaBase,
    SkillStructuredResponse,
)

from ..brain.brain_types import (
    SituationBuilderFn,
)
from ..agent.agent_base import AgentBase

from ..team import (
    TeamBase,
    SupervisionStrategy,
)

from .crew_base import (
    CrewBase,
    CrewInputFresh,
    CrewInputClarification,
)
from ..json_serializar_from_custom_models import (
    JsonSerializarFromCustomModels
)

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


class TransferBrainSchema(
    BrainSchemaBase,
    Serializable
):
    from_account: str
    to_account: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @classmethod
    def lc_id(cls) -> list[str]:
        """A unique identifier for this class for serialization purposes.

        The unique identifier is a list of strings that describes the path
        to the object.
        For example, for the class `langchain.llms.openai.OpenAI`, the id is
        ["langchain", "llms", "openai", "OpenAI"].
        """
        # Pydantic generics change the class name.
        # So we need to do the following
        if (
            "origin" in cls.__pydantic_generic_metadata__
            and cls.__pydantic_generic_metadata__["origin"] is not None
        ):
            original_name = cls.__pydantic_generic_metadata__[
                "origin"
            ].__name__
        else:
            original_name = cls.__name__
        return [*cls.get_lc_namespace(), original_name]

    @property
    def lc_attributes(self) -> Dict:
        return {
            "from_account": self.from_account,
            "to_account": self.to_account
        }


class TransferClarification(ClarificationSchemaBase):
    confirmation: Literal['y', 'n']


class TransferInput(SkillInputSchemaBase):
    from_account: str
    to_account: str
    confirmation: Literal['y', 'n']


class TransferOutput(
    ResultSchemaBase,
    Serializable
):
    result: str
    new_balance: int

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "result": self.result,
            "new_balance": self.new_balance
        }


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


list_items_computation: Skill = SkillStructuredResponse(
    name='list_items',
    description=(
        'shows a list of items in a structured format for the user \n'
        'use this tool when a user anwser for list of items'
    ),
    brain_schema=ListItemsInput
)


class TransferSkill(
    SkillComputationWithClarification[
        TransferBrainSchema,
        TransferClarification,
        TransferInput,
        TransferOutput,
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


def situation_builder(input, config):
    return 'keep focus'


tools_availables = [
    sum_computation,
    list_items_computation,
    TransferSkill(),
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
            ¿Qué quieres saber sobre finanzas o matemáticas?

    user: Cuál es el planeta más lejano del sol?

    agent: send the question to other colleague expert in astronomy

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
    options: List[Skill] = []


class AgentSupervisor(AgentBase):
    name: str = 'Pablo'
    job_description: str = '''
    Select the best team member to answer the user's question
    '''

    public_bio: str = '''
    You are a agent who work in a team trying to answer the questions
    from {user_name}.

    Engage in small talk.

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
def checkpointer():
    serde = JsonSerializarFromCustomModels(
        valid_namespaces=['crew_builder']
    )
    fake_service = MemorySaver(
        serde=serde
    )
    yield fake_service


@pytest.fixture
def config_runtime(llm_srv, use_cases_srv, checkpointer):
    def _config_runtime(thread_id: str):
        return RunnableConfig(
            configurable={
                "llm_srv": llm_srv,
                "use_cases_srv": use_cases_srv,
                "user_name": "Pedrito",
                "today": datetime.now().isoformat(),
                "checkpointer": checkpointer,
                "base_srv_for_transfer": use_cases_srv,
                "base_srv_for_sum": use_cases_srv,
                "thread_id": thread_id
            },
            recursion_limit=10
        )
    return _config_runtime


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


@pytest.fixture
def crew_base(team_base):
    crew = CrewBase(
        team=team_base
    )
    return crew


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_what_is_my_name(crew_base, config_runtime):
    message = UserMessage(
        id='11111',
        timestamp=datetime.now().isoformat(),
        content='hola, cuál es mi nombre?'
    )
    input = CrewInputFresh(
        message=message
    )
    thread_id = "11111"
    result = await crew_base.ainvoke(input, config_runtime(thread_id))
    assert isinstance(result, CollaboratorOutputResponse)
    content = result.message.content
    assert 'Pedrito' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_remember_previous_message(crew_base, config_runtime):
    thread_id = "222222"
    message = UserMessage(
        id=thread_id,
        timestamp=datetime.now().isoformat(),
        content='hola, ahora estoy en la ciudad de Budapest'
    )
    input = CrewInputFresh(
        message=message
    )
    result = await crew_base.ainvoke(input, config_runtime(thread_id))
    assert isinstance(result, CollaboratorOutputResponse)
    message.content = 'Recuerdas en qué ciudad estoy?'
    result = await crew_base.ainvoke(input, config_runtime(thread_id))
    assert isinstance(result, CollaboratorOutputResponse)
    content = result.message.content
    assert 'Budapest' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_structured_response(crew_base, config_runtime):
    message = UserMessage(
        id='22222',
        timestamp=datetime.now().isoformat(),
        content=(
            'Dile a Adam_Smith que quiero ver una lista de los tipos'
            ' de cuenta bancaria que existen?'
        )
    )
    input = CrewInputFresh(
        message=message
    )
    config_with_thread = config_runtime(thread_id="3333")
    result = await crew_base.ainvoke(input, config_with_thread)
    assert isinstance(result, CollaboratorOutputResponseStructured)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_clarification_complete(crew_base, config_runtime):
    # Hacemos una petición que retorna un clarification request
    message = UserMessage(
        id='22222',
        timestamp=datetime.now().isoformat(),
        content=(
            'Usando tool "transfer_money" Haz una transferencia de 25$  '
            ' de mi cuenta corriente a mi cuenta de ahorro'
        )
    )
    input = CrewInputFresh(
        message=message
    )
    config_with_thread = config_runtime(thread_id="44444")
    result = await crew_base.ainvoke(input, config_with_thread)
    assert isinstance(result, CollaboratorOutputClarification)
    # Respondemos la clarificación
    requested = result.clarification_requested
    message = ClarificationSimpleMessage(
        payload={"confirmation": "y"},
        computation_id=requested.clarification_id,
        timestamp=datetime.now().isoformat(),
        content=""
    )
    input = CrewInputClarification(
        clarification_message=message
    )
    result = await crew_base.ainvoke(input, config_with_thread)
    assert isinstance(result, CollaboratorOutputResponse)


# @pytest.mark.only
@pytest.mark.asyncio
async def test_clarification_non_existent(crew_base, config_runtime):
    message = ClarificationSimpleMessage(
        payload={"confirmation": "y"},
        computation_id="2222222222222",
        timestamp=datetime.now().isoformat(),
        content=""
    )
    input = CrewInputClarification(
        clarification_message=message
    )
    config_with_thread = config_runtime(thread_id="55555")
    with pytest.raises(ValueError) as exc_info:
        await crew_base.ainvoke(input, config_with_thread)
    assert str(exc_info.value).startswith('There is no clarification')


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_stream_what_is_my_name(crew_base, config_runtime):
    message = UserMessage(
        id='11111',
        timestamp=datetime.now().isoformat(),
        content='hola, cuál es mi nombre?'
    )
    input = CrewInputFresh(
        message=message
    )
    thread_id = "11111"
    events = []
    async for event in crew_base.astream_events(
        input,
        config=config_runtime(thread_id),
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
