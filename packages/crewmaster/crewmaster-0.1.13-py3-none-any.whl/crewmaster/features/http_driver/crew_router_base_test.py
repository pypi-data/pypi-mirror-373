from datetime import datetime
import json
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
from fastapi.testclient import TestClient
from pydantic_settings import (
    SettingsConfigDict,
)
from ...core.pydantic import (
    BaseModel,
    Field,
)
from langchain_core.load.serializable import Serializable
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from ..collaborator import (
    UserMessage,

)
from ..skill import (
    Skill,
    BrainSchemaBase,
    ClarificationSchemaBase,
    SkillInputSchemaBase,
    ResultSchemaBase,
    SkillComputationDirect,
    SkillComputationWithClarification,
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
from ..crew.crew_base import (
    CrewBase,
)

from .crew_router_base import (
    CrewRouterBase,
)
from .crew_settings import CrewSettings
from .crew_dependencies import CrewDependencies

from .auth import (
    # GoogleAuthStrategy,
    PublicAccessStrategy,
    UserLogged,
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


class TransferBrainSchema(BrainSchemaBase, Serializable):
    from_account: str
    to_account: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

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


class TransferOutput(ResultSchemaBase):
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


class TransferSkill(
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
    skill_input_schema: Type[TransferInput] = TransferInput
    result_schema: Type[TransferOutput] = TransferOutput
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
        log.info('servicio de transfer:', s=config)
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
            **brain_input.dict(),
            **clarification_input.dict()
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
    job_description: str = '''
    Answer questions about Finance and Mathematics.
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

    user: Cuánto es 10 + 10?
    agent: 20

    """
    options: List[Skill] = tools_availables

    situation_builder: Optional[SituationBuilderFn] = situation_builder


class AgentCervantes(AgentBase):
    name: str = 'Cervantes'
    job_description: str = '''
    Answer questions about literature
    '''

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
            ¿Qué quieres saber sobre finanzas o matemáticas?

    user: Quién escribió cien años de soledad?
    agent: Gabriel García Marquez

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

    '''
    directives: str = '''
    Use three sentences maximum and keep the answer as concise as possible.

    You speak exclusively in Spanish and always maintain a friendly,
    humorous tone, sometimes with a touch of
    sarcasm to keep the conversation lively and engaging.

    '''
    examples: str = """
    Here is an example interaction to illustrate your style:

    user: Hola, como estás?
    agent: ¡Hola {user_name}! Estoy tan bien que hasta \
            el café se pone celoso. \
            ¿En que te puedo ayudar hoy?


    """
    options: List[Skill] = []


class Settings(CrewSettings):
    """
    Clase de Pydantinc para manejar los settings

    Ver: https://fastapi.tiangolo.com/advanced/settings/
    """
    app_name: str = "Timelog servidor para Chatbot"
    app_version: str = '0.03'
    app_summary: str = "Servidor para manejo de agentes"
    app_root_path: str = "/"
    auth_client_id: str = ""
    auth_client_secret: str = ""
    auth_token_uri: str = "https://www.googleapis.com/oauth2/v3/token"
    # Id de la hoja de google dónde se encuentra la configuración
    config_sheet_id: str = ""
    # api key para Open AI
    llm_api_key_open_ai: str = ""
    llm_model_open_ai: str = ""
    llm_temperature_open_ai: int = 0
    # datos para la conexión al vector store en postgress
    pg_database: str = ""
    pg_username: str = ""
    pg_password: str = ""
    pg_port: str = "5432"
    pg_server: str = ""
    # Configuración de los embeddings
    embeddings_collection_name: str = ""
    embeddings_model: str = ""

    model_config = SettingsConfigDict(
        extra="allow",
        env_file="../../../.env"
    )


@pytest.fixture
def reset_sse_starlette_appstatus_event():
    """
    Fixture that resets the appstatus event in the sse_starlette app.

    Should be used on any test that uses sse_starlette to stream events.
    """
    # See https://github.com/sysid/sse-starlette/issues/59
    from sse_starlette.sse import AppStatus

    AppStatus.should_exit_event = None


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


@pytest.fixture
def build_settings():
    yield Settings()


@pytest.fixture
def setup_router(build_settings, crew_base):
    # auth_strategy = GoogleAuthStrategy(
    #     token_uri=build_settings.auth_token_uri,
    #     client_id=build_settings.auth_client_id,
    #     client_secret=build_settings.auth_client_secret
    # )

    auth_strategy = PublicAccessStrategy()

    def base_srv_for_transfer_provider(
        user_logged: UserLogged
    ):
        return (
            'servicio de transferencia '
            f'para usuario {user_logged.name}'
        )

    def base_srv_for_sum_provider():
        return 'yo soy un servicio de transferencia'

    class CustomDependency(BaseModel):
        base_srv_for_transfer: str
        base_srv_for_sum: str

    async def custom_injector(
        settings: CrewSettings,
        known: CrewDependencies
    ):
        user_logged = known.user_logged
        srv_for_sum = base_srv_for_sum_provider()
        srv_for_transfer = base_srv_for_transfer_provider(
            user_logged=user_logged
        )
        return CustomDependency(
            base_srv_for_sum=srv_for_sum,
            base_srv_for_transfer=srv_for_transfer
        )

    router = CrewRouterBase(
        runnable=crew_base,
        settings=build_settings,
        dependencies_factory=custom_injector,
        auth_strategy=auth_strategy
    )
    yield router.fastapi_router


@pytest.fixture
def http_client(
    setup_router,
    reset_sse_starlette_appstatus_event
):
    client = TestClient(
        app=setup_router
    )
    yield client


@pytest.fixture
def build_metadata():
    def _config_metadata(thread_id: str):
        return {
            "thread_id": thread_id
        }
    yield _config_metadata


# @pytest.mark.only
@pytest.mark.asyncio
async def test_stream_simple_fresh(
    http_client,
    build_metadata,
):
    user_message = {
        "id": "2222",
        "timestamp": datetime.now().isoformat(),
        "content": "hola"
    }
    user_input = {
        "type": "http.input.fresh",
        "message": user_message
    }
    thread_id = "11111"
    metadata = build_metadata(thread_id)
    event_filter = {
        "scope": 'answer',
        "moments": ['end'],
        "format": 'compact'
    }
    data = {
        "data": user_input,
        "metadata": metadata,
        "event_filter": event_filter
    }
    serialized = json.dumps(data)
    headers = {"Authorization": "churrinPeladinDeTokencin"}
    response = http_client.post(
        "/crew_events",
        data=serialized,
        headers=headers
    )
    assert response.status_code == 200
    assert 'event: error' not in response.text
    assert 'event: data' in response.text
    assert 'event: end' in response.text


# @pytest.mark.only
@pytest.mark.asyncio
async def test_stream_simple_clarification(
    http_client,
    build_metadata,
):
    user_message = {
        "payload": {"confirmation": "y"},
        "computation_id": "222222",
        "timestamp": datetime.now().isoformat(),
        "content": ""
    }
    user_input = {
        "type": "http.input.clarification",
        "clarification_message": user_message
    }
    thread_id = "11111"
    metadata = build_metadata(thread_id)
    data = {
        "data": user_input,
        "metadata": metadata,
        "token": "yoSoyUnTokenDelBody",
    }
    serialized = json.dumps(data)
    REFRESH_TOKEN = "ChurroToken"
    headers = {"Authorization": REFRESH_TOKEN}
    response = http_client.post(
       "/crew_events",
       data=serialized,
       headers=headers
    )
    assert response.status_code == 200
    assert 'There is no clarification pending' in response.text
