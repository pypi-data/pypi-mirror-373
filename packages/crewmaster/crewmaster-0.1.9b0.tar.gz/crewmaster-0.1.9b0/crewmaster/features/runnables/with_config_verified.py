from abc import abstractmethod
from typing import (
    Any,
    AsyncIterator,
    Optional,
    TypeVar,
)

import structlog

from ...core.pydantic import (
    BaseModel,
)
from langchain_core.runnables.config import (
    ensure_config
)
from langchain_core.load import dumpd
from langchain_core.callbacks.manager import (
    CallbackManagerForChainRun
)
from langchain_core.runnables.config import (
    get_callback_manager_for_config,
)
from langchain_core.runnables import (
    RunnableSerializable,
    RunnableConfig,
)

from .injection_exception import InjectionException


log = structlog.get_logger()
"Loger para el módulo"


Input = TypeVar('Input', bound=BaseModel)
Output = TypeVar('Output', bound=BaseModel)
"""Tipos genéricos para la mixins de configuracion verificada"""


class WithInvokeConfigVerified(
    RunnableSerializable[Input, Output]
):
    def _verify_runtime_config(
        self,
        config: RunnableConfig
    ) -> BaseModel:
        try:
            config = ensure_config(config)
            # Buscamos el esquema para validar la configuración en runtime
            config_schema = self.config_schema()
            # Verificamos que la configuración tenga los campos requeridos
            parsed = config_schema.model_validate(config)
            return parsed
        except InjectionException as error:
            error.add_note((
                'Runtime config has errors, '
                'please ensure dependencies are injected'
            ))
            raise

    @abstractmethod
    def invoke_config_parsed(
        self,
        input: Input,
        config_parsed: BaseModel,
        config_raw: Optional[RunnableConfig] = None
    ) -> Output:
        pass

    def invoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None
    ) -> Output:
        config = ensure_config(config)
        config_parsed = self._verify_runtime_config(config)
        result = self.invoke_config_parsed(
            input=input,
            config_parsed=config_parsed,
            config_raw=config
        )
        return result


class WithAsyncStreamConfigVerified(
    RunnableSerializable[Input, Output]
):
    def _verify_runtime_config(
        self,
        config: RunnableConfig
    ) -> BaseModel:
        try:
            config = ensure_config(config)
            # Buscamos el esquema para validar la configuración en runtime
            config_schema = self.config_schema()
            # Verificamos que la configuración tenga los campos requeridos
            parsed = config_schema.parse_obj(config)
            return parsed
        except InjectionException as error:
            error.add_note((
                'Runtime config has errors, '
                'please ensure dependencies are injected'
            ))
            raise

    @abstractmethod
    async def astream_config_parsed(
        self,
        input: Input,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
        run_manager: CallbackManagerForChainRun,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        pass

    async def astream(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[Output]:
        config = ensure_config(config)
        config_parsed = self._verify_runtime_config(config)
        callback_manager = get_callback_manager_for_config(config)
        run_manager = callback_manager.on_chain_start(
            serialized=dumpd(self),
            inputs=input.model_dump(),
            name=self.name
        )
        iterator = self.astream_config_parsed(
            input=input,
            config_parsed=config_parsed,
            config_raw=config,
            run_manager=run_manager,
            **kwargs,
        )
        async for chunk in iterator:  # type: ignore
            yield chunk


class WithAsyncInvokeConfigVerified(
    RunnableSerializable[Input, Output]
):
    def _verify_runtime_config(
        self,
        config: RunnableConfig
    ) -> BaseModel:
        try:
            config = ensure_config(config)
            # Buscamos el esquema para validar la configuración en runtime
            config_schema = self.config_schema()
            # Verificamos que la configuración tenga los campos requeridos
            parsed = config_schema.model_validate(config)
            return parsed
        except InjectionException as error:
            error.add_note((
                'Runtime config has errors, '
                'please ensure dependencies are injected'
            ))
            raise

    @abstractmethod
    async def async_invoke_config_parsed(
        self,
        input: Input,
        config_parsed: BaseModel,
        config_raw: Optional[RunnableConfig] = None
    ) -> Output:
        pass

    async def ainvoke(
        self,
        input: Input,
        config: Optional[RunnableConfig] = None
    ) -> Output:
        config = ensure_config(config)
        config_parsed = self._verify_runtime_config(config)
        result = await self.async_invoke_config_parsed(
            input=input,
            config_parsed=config_parsed,
            config_raw=config
        )
        return result
