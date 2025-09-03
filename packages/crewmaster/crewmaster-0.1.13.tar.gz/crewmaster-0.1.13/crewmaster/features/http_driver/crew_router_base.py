from enum import Enum
from datetime import datetime
from typing import (
    Annotated,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
)
import structlog
from ...core.pydantic import (
    BaseModel,
)
from pydantic import (
    BaseModel as BaseModelV2,
    ConfigDict,
)
from fastapi import (
    APIRouter,
    Body,
    Depends,
)
from sse_starlette import (
    EventSourceResponse,
)
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.language_models import (
    BaseChatModel,
)
from langchain_core.runnables import (
    Runnable,
)
from langchain_core.runnables.config import (
    merge_configs,
)
from langgraph.checkpoint.base import (
    BaseCheckpointSaver
)
from ..crew import (
    CrewInput,
    CrewInputAdapter,
)
from .http_input import (
    HttpInput,
    HttpMetadata,
    HttpEventFilter,
)
from .auth import (
    AuthStrategyInterface,
    UserLogged,
    PublicAccessStrategy,
)
from .factories import (
    chatopenai_factory,
    memory_factory,
)
from .crew_settings import (
    CrewSettings
)
from .crew_dependencies import (
    CrewDependencies,
)
from .stream_conversor import (
    stream_conversor,
)

text_stream_content_type: Dict[int | str, Dict[str, Any]] = {200: {"content": {
        "text/event-stream, application/json": {
            "description": "Contenidos devueltos cuándo todo sale bien"
        },
        "application/json": {
            "description": "Contenido devuelto cuándo hay algún error"
        }
    }
}}


log = structlog.get_logger()
"Logger para la clase"


def _build_config_for_runnable(
    metadata: HttpMetadata,
    known_dependencies: Dict[str, Any],
    custom_dependencies: Dict[str, Any]
) -> RunnableConfig:
    """
    Para construir la configuración que pasamos al runnable,
    combinamos lo que viene en la metadata con las dependencias provistas.
    En caso que haya un elemento requerido por la configuración del runnable
    que no esté en las dependencias, se generará un error de validación
    al ejecutar el runnable.
    """
    metadata_raw = metadata.model_dump()
    config_external = RunnableConfig(
        configurable=metadata_raw
    )
    config_known = RunnableConfig(
        configurable=known_dependencies
    )
    if custom_dependencies is not None:
        config_custom = RunnableConfig(
            # configurable=custom_dependencies.model_dump()
            configurable=custom_dependencies
        )
    merged = merge_configs(
        config_external,
        config_known,
        config_custom
    )
    return merged


class CrewRouterBase(BaseModelV2):
    path: str = 'crew_events'
    """Ruta en que se monta el endpoint"""
    runnable: Runnable
    """Runnable que ejecuta el Crew"""
    settings: CrewSettings
    """Settings para el Crew"""
    tags: Optional[List[str | Enum]] = None
    """Etiquetas para categorizar el crew"""
    auth_strategy: AuthStrategyInterface = PublicAccessStrategy()
    "Estrategia de autorización para la aplicación"
    dependencies_factory: Optional[
        Callable[[CrewSettings, CrewDependencies], Awaitable[BaseModel]]
    ] = None
    "Proveedor para dependencias custom de la aplicación"
    checkpointer: BaseCheckpointSaver = memory_factory()
    """Factory para checkpointer que almacena estado del Crew"""
    llm: Optional[
        BaseChatModel
    ] = None
    """Factory para LLM con qué interactúa el Crew"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """Configuración del modelo"""

    def model_post_init(
        self,
        __context: Any
    ):
        """
        Se configuran las factories que no son asignadas por el usuario
        y requieren los settings para configurarse
        """
        if self.llm is None:
            self.llm = chatopenai_factory(
                api_key=self.settings.llm_api_key_open_ai,
                model=self.settings.llm_model_open_ai,
                temperature=self.settings.llm_temperature_open_ai
            )

    async def build_custom_dependencies(
        self,
        known_dependencies: CrewDependencies
    ):
        if self.dependencies_factory is None:
            return None
        deps = await self.dependencies_factory(
            self.settings,
            known_dependencies
        )
        return deps

    def transform_input(
        self,
        original: HttpInput
    ) -> CrewInput:
        """
        Transforma la data de entrada HttpInput
        en la data esperada por el Crew
        """
        data_json = original.model_dump()
        data_json['type'] = data_json['type'].replace('http.', 'crew.')
        crew_input = CrewInputAdapter.validate_python(data_json)
        return crew_input

    @property
    def fastapi_router(
        self
    ) -> APIRouter:
        # Creamos el router de FastApi
        router = APIRouter(
            tags=self.tags,
        )

        @router.post(
            f'/{self.path}',
            responses=text_stream_content_type,
            description="Stream de Events using the SSE protocol"
        )
        async def _stream_events(
            data: Annotated[
                HttpInput,
                Body(embed=True)
            ],
            metadata: Annotated[
                HttpMetadata,
                Body(embed=True)
            ],
            user_logged: Annotated[
                UserLogged,
                Depends(self.auth_strategy.execute)
            ],
            event_filter: Annotated[
                Optional[HttpEventFilter],
                Body(embed=True),
            ] = None,
        ):
            # Transformamos data de entrada en la requerida por el Crew
            crew_input = self.transform_input(data)
            # Construimos el objeto con las dependencias definidas por el Crew
            known_dependencies = CrewDependencies(
                checkpointer=self.checkpointer,
                llm_srv=self.llm,
                user_logged=user_logged,
                user_name=user_logged.name or '',
                today=datetime.now().isoformat(),
            )
            # Construimos las dependencias requeridas por la aplicación
            # se hace hace llamando al injector configurado por la aplicación
            custom_dependencies = await self.build_custom_dependencies(
                known_dependencies=known_dependencies
            )
            # Se mezclan los componentes para la configuración de runtime
            # que se va a pasar al runnable
            config = _build_config_for_runnable(
                metadata=metadata,
                known_dependencies=dict(known_dependencies),
                custom_dependencies=dict(custom_dependencies or {})
            )
            event_filter_default: HttpEventFilter = HttpEventFilter(
                scope='answer',
                moments={'end'},
                format='compact'
            )
            event_filter_applied = event_filter or event_filter_default
            # Se crea el generador de eventos para hacer el streaming
            return EventSourceResponse(
                stream_conversor(
                    runnable=self.runnable,
                    input=crew_input,
                    config=config,
                    scope=event_filter_applied.scope,
                    moments=event_filter_applied.moments,
                    event_format=event_filter_applied.format
                )
            )
        return router
