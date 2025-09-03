import json
import structlog
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Literal,
    Optional,
    Sequence,
    Set,
)
from langchain_core.runnables.schema import (
    StreamEvent,
)
from pydantic import (
    BaseModel
)
from sse_starlette import (
    ServerSentEvent,
)
from langchain_core.runnables import (
    Runnable,
    RunnableConfig,
)
from langserve.serialization import WellKnownLCSerializer

from ..crew import (
    CrewInput,
)


log = structlog.get_logger()
"Loger para el módulo"


def prepare_error_for_client(error: BaseException) -> str:
    """Prepara un error para enviarlo como evento

    Args:
        error (BaseException): Error generado en la aplicación

    Returns:
        str: json con la serializacion del error
    """
    # TODO: Implementar lógica para convertir el error en "problema"
    # stack_trace = traceback.format_exc()
    result = json.dumps(
        {"status_code": 500, "message": str(error)}
    )
    return result


class StreamFilter(BaseModel):
    include_names: Optional[Sequence[str]] = None
    include_tags: Optional[Sequence[str]] = None
    include_types: Optional[Sequence[str]] = None
    exclude_names: Optional[Sequence[str]] = None
    exclude_tags: Optional[Sequence[str]] = None
    exclude_types: Optional[Sequence[str]] = None


ScopeAvailables = Literal[
    'answer',
    'deliberations',
    'computations'
]

EventFormat = Literal[
    'compact',
    'extended'
]


def build_pre_filter(
    scope: ScopeAvailables
) -> StreamFilter:
    names = {
        "answer": ['cbr:crew'],
        "deliberations": ['cbr:crew', 'cbr:agent'],
        "computations": ['cbr:crew', 'cbr:agent', 'cbr:muscle']
    }
    return StreamFilter(
        include_names=names[scope]
    )


AllowedEventMoment = Literal["start", "stream", "end"]


def _strip_internal_keys(
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """Strip out internal metadata keys that should not be sent to the client.

    These keys are defined to be any key that starts with "__".
    """
    return {k: v for k, v in metadata.items() if not k.startswith("__")}


def is_event_required(
    event: StreamEvent,
    allowed_event_moments: Set[AllowedEventMoment],
) -> bool:
    result = any(
        event["event"].endswith(f'_{allowed_type}')
        for allowed_type in allowed_event_moments
    )
    return result


def reduce_event(event):
    event_type = event.get('event', '')
    event_data = event.get('data', {})
    reduced = {
        'event': event_type,
        'data': event_data
    }
    return reduced


def create_sse_event(
    event: StreamEvent,
    event_format: EventFormat,
    serializer
) -> ServerSentEvent:
    event["metadata"] = _strip_internal_keys(event.get("metadata", {}))
    event_transformed = (event if event_format == 'extended'
                         else reduce_event(event))
    serialized_body = serializer.dumps(event_transformed).decode("utf-8")
    sse_event = ServerSentEvent(
        event="data",
        data=serialized_body
    )
    return sse_event


async def stream_conversor(
    runnable: Runnable,
    input: CrewInput,
    config: RunnableConfig,
    scope: ScopeAvailables = 'answer',
    moments: Set[AllowedEventMoment] = {'end'},
    event_format: EventFormat = 'compact'
) -> AsyncIterator[ServerSentEvent]:
    """Conversor de eventos para el stream del Crew

    Args:
        runnable (Runnable): runnable que se quiere convertir los eventos
        input (HttpInput): Data de entrada al runnable
        config (RunnableConfig): configuración para el runnable

    Returns:
        AsyncIterator[ServerSentEvent]: Generador de eventos convertidos

    Yields:
        Iterator[AsyncIterator[ServerSentEvent]]: Iterador de los eventos
    """
    serializer = WellKnownLCSerializer()
    try:
        filter = build_pre_filter(scope).model_dump()
        async for event_original in runnable.astream_events(
            input=input,
            config=config,
            version="v2",
            **filter
        ):
            if is_event_required(
                event_original,
                allowed_event_moments=moments
            ):
                event_sse = create_sse_event(
                    event_original,
                    event_format,
                    serializer
                )
                yield event_sse
            else:
                continue
        # Una vez finalizado el stream
        # enviamos el evento de fin del SSE
        yield ServerSentEvent(event="end")
    except BaseException as error:
        error_data = prepare_error_for_client(error)
        yield ServerSentEvent(
            event="error",
            data=error_data
        )
        # En el iterator que usan en ApiHandler, hacen un raise en esta línea.
        # Cuándo hago el raise se me genera un error no capturado.
        # Viendo en la documentación de SSE-Startlette se debe hacer return
        # ver: https://github.com/sysid/sse-starlette/blob/207e770d9dbf30fde7effb59e094a68d291e4eb4/examples/error_handling.py#L9  # noqa: E501
        # Por eso lo cambié de raise a return
        return
