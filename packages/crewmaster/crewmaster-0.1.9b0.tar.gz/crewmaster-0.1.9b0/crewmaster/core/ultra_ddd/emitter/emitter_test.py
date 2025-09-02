import structlog
import pytest
import operator

from .emitter import Emitter

log = structlog.get_logger()
"Logger para el módulo"


@pytest.mark.only
@pytest.mark.asyncio
async def test_single_value_as_stream():
    emitter = Emitter[str]()
    emitter.emit_value('hola')
    async for value in emitter.get_stream():
        result = value
    assert result == 'hola'


@pytest.mark.only
@pytest.mark.asyncio
async def test_multiple_value_as_stream():
    emitter = Emitter[str]()
    emitter.emit_value('hola, ', finished=False)
    emitter.emit_value('como estas?')
    result = ''
    async for value in emitter.get_stream():
        result += value
    assert result == 'hola, como estas?'


@pytest.mark.only
@pytest.mark.asyncio
async def test_single_value_as_single():
    emitter = Emitter[str]()
    emitter.emit_value('hola')
    result = await emitter.get_value()
    assert result == 'hola'


@pytest.mark.only
@pytest.mark.asyncio
async def test_multiple_value_acummulated():
    emitter = Emitter[str](
        operator=operator.add
    )
    emitter.emit_value('hola, ', finished=False)
    emitter.emit_value('buen dia, ', finished=False)
    emitter.emit_value('como estas?')
    result = await emitter.get_value()
    assert result == 'hola, buen dia, como estas?'
