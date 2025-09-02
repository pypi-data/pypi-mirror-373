import structlog
import pytest

from .emitter_explained import (
    EmitterExplained,
)
from ...ultra_result.either import (
    right,
    left,
)

log = structlog.get_logger()
"Logger para el módulo"


@pytest.mark.only
@pytest.mark.asyncio
async def test_single_value_as_stream():
    emitter = EmitterExplained[str, None](
        right_explanation_fn='Estoy bien'
    )
    emitter.emit_value(right(None))
    async for value in emitter.get_stream():
        result = value
    assert result.get('explanation', '') == 'Estoy bien'


@pytest.mark.only
@pytest.mark.asyncio
async def test_fn_transform_right():
    emitter = EmitterExplained[Exception, str](
        right_explanation_fn=lambda result: f'Hola {result}'
    )
    emitter.emit_value(right('Pedro'))
    result = await emitter.get_value()
    assert result.get('explanation', '') == 'Hola Pedro'


@pytest.mark.only
@pytest.mark.asyncio
async def test_exclusive_left():
    emitter = EmitterExplained[Exception, str](
        right_explanation_fn=lambda result: f'Hola {result}',
        left_exclusive={ValueError: 'Sucedio un problemon'}
    )
    emitter.emit_value(left(ValueError('invalid value')))
    result = await emitter.get_value()
    assert result.get('explanation', '') == 'Sucedio un problemon'


@pytest.mark.only
@pytest.mark.asyncio
async def test_multiples_errors():
    emitter = EmitterExplained[Exception, str](
        right_explanation_fn=lambda result: f'Hola {result}',
        left_exclusive={ValueError: 'Sucedio un problemon'}
    )
    emitter.emit_value(left([
        ValueError('invalid value'),
        Exception('otro error más')
    ]))
    result = await emitter.get_value()
    explanation = result.get('explanation', '')
    assert (
        'Can not process because 2 problems'
        in explanation
    )
    assert 'invalid value' in explanation
    assert 'otro error más' in explanation


@pytest.mark.only
@pytest.mark.asyncio
async def test_multiples_errors_with_custom_intro():
    emitter = EmitterExplained[Exception, str](
        right_explanation_fn=lambda result: f'Hola {result}',
        left_multiple_intro='Increible, hay {count} errores:'
    )
    emitter.emit_value(left([
        ValueError('invalid value'),
        Exception('otro error más')
    ]))
    result = await emitter.get_value()
    explanation = result.get('explanation', '')
    assert (
        'Increible, hay 2 errores:'
        in explanation
    )
    assert 'invalid value' in explanation
    assert 'otro error más' in explanation
