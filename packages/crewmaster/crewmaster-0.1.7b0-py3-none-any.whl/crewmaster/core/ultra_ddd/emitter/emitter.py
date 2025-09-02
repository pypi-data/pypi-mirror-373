from asyncio import (
    Queue,
)
from typing import (
    AsyncIterator,
    Callable,
    Optional,
    TypeVar,
    Generic,
)


# Define generic type variables
OutputType = TypeVar('OutputType')


class NoEmittedValue(Exception):
    pass


EmitterOperator = Callable[
    [OutputType, OutputType],
    OutputType
]


class Emitter(Generic[OutputType]):
    """
    Abstract base class for emitter.

    """
    _queue = Queue()
    _is_finished = False
    operator: Optional[EmitterOperator] = None
    """
    Operador utilizado para el acumular los valores en get_value,
    por defecto se envía siempre el último valor del stream
    """

    def __init__(
        self,
        operator: Optional[EmitterOperator] = None
    ):
        self.operator = operator

    def emit_value(
        self,
        value: OutputType,
        finished: bool = True
    ) -> None:
        self._queue.put_nowait(value)
        if finished:
            self._queue.put_nowait(None)
            self._is_finished = True

    async def get_stream(
        self,
    ) -> AsyncIterator[OutputType]:
        while not self._is_finished or not self._queue.empty():
            result = await self._queue.get()
            if result is None:
                break
            yield result

    def _acum(
        self,
        current: Optional[OutputType],
        next: OutputType
    ) -> OutputType:
        # Por defecto siempre enviamos el último valor
        if self.operator is None:
            return next
        return self.operator(current, next)

    async def get_value(
        self,
    ) -> OutputType:
        response = None
        async for result in self.get_stream():
            if response is None:
                response = result
            else:
                response = self._acum(response, result)
        if response is None:
            raise NoEmittedValue('No value emitted')
        return response
