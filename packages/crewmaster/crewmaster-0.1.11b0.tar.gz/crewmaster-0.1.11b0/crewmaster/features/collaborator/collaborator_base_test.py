import json
import os
import pytest
import structlog
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()  # Carga las variables desde .env
from ...core.pydantic import (
    SecretStr,
    BaseModel,
)

from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_openai import ChatOpenAI
from langgraph.graph.state import (
    StateGraph,
)
from .collaborator_input import (
    CollaboratorInputFresh,
)
from .collaborator_ouput import (
    CollaboratorOutputResponse,
)
from .state import (
    CollaboratorState,
)

from .collaborator_base import CollaboratorBase
from .team_membership import (
    TeamMembership,
)
from .message import (
    UserMessage,
    AgentMessage,
)

from dotenv import load_dotenv
load_dotenv()  # Carga las variables desde .env

log = structlog.get_logger()
"Loger para el módulo"


class CollabFake(CollaboratorBase):
    name: str = "raul_collaborator"
    job_description: str = "Probar que todo esté bien"

    def join_team(
        self,
        team_membership: TeamMembership
    ):
        pass

    def _build_graph(
        self,
        graph: StateGraph,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
    ):
        def executor(input: CollaboratorState):
            output = CollaboratorOutputResponse(
                message=AgentMessage(
                    content="Hola, todo bien por aqui",
                    to="User",
                    author="SuperAgent"
                )
            )
            return {
                "output": output
            }
        graph.add_node(executor)
        graph.set_entry_point('executor')
        return graph


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
        },
        recursion_limit=10
    )


@pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_hello(config_runtime):
    collab = CollabFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='hola'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    # input_dict = dict(input)
    result = await collab.ainvoke(input, config_runtime)
    assert isinstance(result, CollaboratorOutputResponse)


@pytest.mark.asyncio
@pytest.mark.llm_evaluation
@pytest.mark.only
async def test_stream_hello(config_runtime):
    collab = CollabFake()
    message = UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content='hola'
    )
    input = CollaboratorInputFresh(
        message=message
    )
    events = []
    async for event in collab.astream_events(
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
