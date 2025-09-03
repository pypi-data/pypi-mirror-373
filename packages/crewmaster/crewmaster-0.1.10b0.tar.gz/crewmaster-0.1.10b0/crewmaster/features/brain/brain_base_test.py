import json
import os
from typing import Any, Dict, List, Literal, Optional, Type

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
    Colleague,
    UserMessage,
)
from ..skill import (
    BrainSchemaBase,
    ResultSchemaBase,
    Skill,
    SkillComputationDirect,
    SkillStructuredResponse,
    SkillContribute,
)
from .brain_types import (
    BrainOutputComputationsRequired,
    BrainOutputContribution,
    BrainOutputResponse,
    BrainOutputResponseStructured,
    BrainInputFresh,
    SituationBuilderFn,
)
from .brain_base import (
    BrainBase
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


send_message_to_colleague = SkillContribute(
    name='send_message_to_colleague',
    description='Send a message to a colleague',
)


def situation_builder(input, config):
    return 'keep focus'


your_name = "Your name is Adam_Smith"

job_description = '''
Answer questions only about Finance and Mathematics.
'''

public_bio = '''
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

directives = '''


Use three sentences maximum and keep the answer as concise as possible.

You speak exclusively in Spanish and always maintain a friendly,
humorous tone, sometimes with a touch of
sarcasm to keep the conversation lively and engaging.

Remember to always address {user_name} by their name, \
keep the conversation light and engaging.
'''
examples = """
Here is an example interaction to illustrate your style:

user: Hola, como estás?

agent: ¡Hola {user_name}! Estoy tan bien que hasta \
        el café se pone celoso. \
        ¿Qué quieres saber sobre finanzas o matemáticas?

user: Cuál es el planeta más lejano del sol?

agent: send the question to other colleague expert in astronomy

"""

colleagues_intro: str = (
    'You are part of a team of colleagues.'
    'Please use tool if you need to send a message to anyone.\n\n'
    '"""Colaborators:"""'
)

colleagues: List[Colleague] = [
        Colleague(
            name='Cervantes',
            job_description='Answer questions about Literature'
        ),
        Colleague(
            name='Sagan',
            job_description='Answer questions about Astronomy'
        ),
    ]
list = [f'{person.name}: {person.job_description}'
        for person in colleagues]
colleagues_str = '\n'.join(list)

instructions = '\n\n'.join([
    your_name,
    public_bio,
    directives,
    job_description,
    colleagues_intro,
    colleagues_str,
    examples,
])


class BrainFake(BrainBase):
    agent_name: str = "Adam_Smith"
    instructions: str = instructions
    skills: List[Skill] = [
        send_message_to_colleague,
        sum_computation,
        list_items_computation,
    ]
    situation_builder: Optional[SituationBuilderFn] = situation_builder


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
def config_runtime(llm_srv):
    config = RunnableConfig(
        configurable={
            "llm_srv": llm_srv
        }
    )
    # Add finalizer to reset mock after each test
    yield config


# @pytest.mark.only
@pytest.mark.llm_evaluation
def test_hello(config_runtime):
    # Crear un diccionario a partir de os.environ
    brain = BrainFake()
    message = create_message('hola, cuál es mi nombre?')
    input = BrainInputFresh(
        messages=[message],
        user_name='Cheito',
        today=datetime.now().isoformat()
    )
    result = brain.invoke(input, config_runtime)
    assert isinstance(result, BrainOutputResponse)
    content = result.message.content
    assert 'Cheito' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
def test_computation_required(config_runtime):
    brain = BrainFake()
    message = create_message('cuánto es 3 + 3?')
    input = BrainInputFresh(
        messages=[message],
        user_name='cheito',
        today=datetime.now().isoformat()
    )
    result = brain.invoke(input, config_runtime)
    assert isinstance(result, BrainOutputComputationsRequired)


# @pytest.mark.only
@pytest.mark.llm_evaluation
def test_contribution(config_runtime):
    brain = BrainFake()
    message = create_message(
        'Una pregunta de literatura, '
        'quién escribió la novela 100 martirios insoportables?'
    )
    input = BrainInputFresh(
        messages=[message],
        user_name='cheito',
        today=datetime.now().isoformat()
    )
    result = brain.invoke(input, config_runtime)
    assert isinstance(result, BrainOutputContribution)


# @pytest.mark.only
@pytest.mark.llm_evaluation
def test_response_structured(config_runtime):
    brain = BrainFake()
    message = create_message(
        'Quiero ver una lista de los tipos'
        ' de cuenta bancaria que existen?'
    )
    input = BrainInputFresh(
        messages=[message],
        user_name='cheito',
        today=datetime.now().isoformat()
    )
    result = brain.invoke(input, config_runtime)
    assert isinstance(result, BrainOutputResponseStructured)


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_stream_hello(config_runtime):
    brain = BrainFake()
    message = create_message('hola, cuál es mi nombre?')
    input = BrainInputFresh(
        messages=[message],
        user_name='Cheito',
        today=datetime.now().isoformat()
    )
    events = []
    async for event in brain.astream_events(
        input,
        config=config_runtime,
        version="v2",
    ):
        events.append(event)
    assert len(events) > 4
    last_event = events[-1]
    assert last_event.get('event') == 'on_chain_end'
    result = last_event.get('data', {}).get('output')
    assert isinstance(result, BrainOutputResponse)
    content = result.message.content
    assert 'Cheito' in content


# @pytest.mark.only
@pytest.mark.llm_evaluation
@pytest.mark.asyncio
async def test_stream_computation_requested(config_runtime):
    brain = BrainFake()
    message = create_message('cuánto es 3 + 3?')
    input = BrainInputFresh(
        messages=[message],
        user_name='Cheito',
        today=datetime.now().isoformat()
    )
    events = []
    async for event in brain.astream_events(
        input,
        config=config_runtime,
        version="v2",
    ):
        events.append(event)
    assert len(events) > 4
    last_event = events[-1]
    assert last_event.get('event') == 'on_chain_end'
    result = last_event.get('data', {}).get('output')
    assert isinstance(result, BrainOutputComputationsRequired)


# @pytest.mark.only
@pytest.mark.asyncio
async def test_get_skills_brain_schema(config_runtime):
    brain = BrainFake()
    skills_map = brain.get_skills_as_dict()
    assert isinstance(skills_map, Dict)
    assert 'sum' in skills_map.keys()
    assert skills_map['sum'].brain_schema == SumInput
