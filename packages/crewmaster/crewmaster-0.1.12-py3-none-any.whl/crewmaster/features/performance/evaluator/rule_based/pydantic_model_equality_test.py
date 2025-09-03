import pytest
import structlog
from .....core.pydantic import (
    BaseModel,
)
from .pydantic_model_equality import (
    PydanticModelEquality,
)

log = structlog.get_logger()
"Loger para el módulo"


class MyModel(BaseModel):
    from_account: str
    to_account: str


@pytest.fixture
def evaluator():
    return PydanticModelEquality(
        model=MyModel
    )


@pytest.mark.only
@pytest.mark.asyncio
async def test_evaluate_matching_models(evaluator):
    received = {"from_account": "checking", "to_account": "savings"}
    expected = {"from_account": "checking", "to_account": "savings"}

    result = await evaluator.evaluate(
        input="test",
        received=received,
        expected=expected
    )

    assert result.name == "pydantic_model_equality"
    assert result.value is True
    assert result.explanation is None


@pytest.mark.only
@pytest.mark.asyncio
async def test_evaluate_non_matching_models(evaluator):
    received = {"from_account": "checking", "to_account": "savings"}
    expected = {"from_account": "checking", "to_account": "business"}

    result = await evaluator.evaluate(
        input="test",
        received=received,
        expected=expected
    )
    assert result.name == "pydantic_model_equality"
    assert result.value is False
    assert result.explanation is not None


@pytest.mark.only
@pytest.mark.asyncio
async def test_evaluate_invalid_data(evaluator):
    received = {"from_account": "checking"}  # Missing 'to_account'
    expected = {"from_account": "checking", "to_account": "savings"}

    result = await evaluator.evaluate(
        input="test",
        received=received,
        expected=expected
    )

    assert result.name == "pydantic_model_equality"
    assert result.value is False
    assert "\nto_account\n  Field required" in result.explanation


@pytest.mark.only
@pytest.mark.asyncio
async def test_evaluate_alias_name(evaluator):
    received = {"from_account": "checking", "to_account": "savings"}
    expected = {"from_account": "checking", "to_account": "savings"}

    result = await evaluator.evaluate(
        input="test",
        received=received,
        expected=expected,
        alias="custom_alias"
    )

    assert result.name == "custom_alias"
    assert result.value is True
