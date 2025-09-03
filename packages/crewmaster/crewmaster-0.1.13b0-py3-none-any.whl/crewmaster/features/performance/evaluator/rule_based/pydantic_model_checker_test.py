import pytest
import structlog
from .....core.pydantic import (
    BaseModel,
)
from .pydantic_model_checker import (
    PydanticModelChecker,
)

log = structlog.get_logger()
"Loger para el módulo"


class MyModel(BaseModel):
    from_account: str
    to_account: str


@pytest.fixture
def evaluator():
    return PydanticModelChecker(
        model=MyModel
    )


@pytest.mark.only
@pytest.mark.asyncio
async def test_received_none(evaluator):
    input = ''
    received = None
    expected = {"from_account": "corriente", "to_account": "ahorros"}
    evaluation = await evaluator.evaluate(
        input=input,
        received=received,
        expected=expected
    )
    assert evaluation.value is False
    assert evaluation.points == 0
    assert evaluation.explanation is not None
    assert 'Input should be a valid dictionary' in evaluation.explanation


@pytest.mark.only
@pytest.mark.asyncio
async def test_alias_handling(evaluator):
    input = ''
    received = {"from_account": "232323", "to_account": "ahorros"}
    expected = {"from_account": "corriente", "to_account": "ahorros"}
    alias = 'un hombre divertido'
    evaluation = await evaluator.evaluate(
        input=input,
        received=received,
        expected=expected,
        alias=alias
    )
    assert evaluation.value is True
    assert evaluation.name == alias


@pytest.mark.only
@pytest.mark.asyncio
async def test_string_received(evaluator):
    input = ''
    received = "yo soy un string y no un json"
    expected = {"from_account": "corriente", "to_account": "ahorros"}
    evaluation = await evaluator.evaluate(
        input=input,
        received=received,
        expected=expected
    )
    assert evaluation.value is False
    assert evaluation.points == 0
    assert evaluation.explanation is not None
    assert 'Input should be a valid dictionary' in evaluation.explanation


@pytest.mark.only
@pytest.mark.asyncio
async def test_json_invalid(evaluator):
    input = ''
    received = {"from": "nombre incompleto", "to_account": "ahorros"}
    expected = {"from_account": "corriente", "to_account": "ahorros"}
    evaluation = await evaluator.evaluate(
        input=input,
        received=received,
        expected=expected
    )
    assert evaluation.value is False
    assert evaluation.points == 0
    assert evaluation.explanation is not None
    assert '\nfrom_account\n  Field required' in evaluation.explanation


@pytest.mark.only
@pytest.mark.asyncio
async def test_json_valid(evaluator):
    input = ''
    received = {"from_account": "232323", "to_account": "ahorros"}
    expected = {"from_account": "corriente", "to_account": "ahorros"}
    evaluation = await evaluator.evaluate(
        input=input,
        received=received,
        expected=expected
    )
    assert evaluation.value is True
    assert evaluation.points == 100
    assert evaluation.explanation is None
