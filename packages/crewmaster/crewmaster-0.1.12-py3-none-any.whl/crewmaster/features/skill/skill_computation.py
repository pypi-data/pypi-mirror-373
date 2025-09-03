from abc import abstractmethod
from typing import (
    Annotated,
    Generic,
    Optional,
    Type,
    Literal,
    Union,
)
from ...core.pydantic import (
    BaseModel,
    Field,
)
from pydantic import TypeAdapter

import structlog
from langchain_core.load.dump import dumpd

from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.config import (
    get_callback_manager_for_config,
)
from ..runnables import (
    WithAsyncInvokeConfigVerified,
    RunnableStreameable,
)
from .types import (
    ComputationRequestedWithClarification,
    ClarificationSchema,
    ComputationRequested,
    ComputationResult,
    SkillInputSchema,
    BrainSchema,
    ResultSchema,
)

from .skill_base import (
    SkillBase,
)


log = structlog.get_logger()
"Loger para el módulo"


class SkillComputationBase(
    SkillBase[BrainSchema],
    Generic[
        BrainSchema,
        ResultSchema,
    ],
):
    type: Literal['skill.computation'] = 'skill.computation'
    require_clarification: bool = False

    brain_schema: Type[BrainSchema]
    result_schema: Type[ResultSchema]

    def invoke(
        self,
        input: ComputationRequested,
        config: RunnableConfig | None = None
    ) -> ComputationResult[BrainSchema, ResultSchema]:
        raise Exception('Tool can only be called asynchronously')

    def get_output_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[ResultSchema]:
        return self.result_schema

    def get_input_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[BrainSchema]:
        return self.brain_schema

    @abstractmethod
    async def async_invoke_config_parsed(
        self,
        input:
            Union[
                ComputationRequested,
                ComputationRequestedWithClarification
            ],
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> ComputationResult:
        ...


class SkillComputationDirect(
    SkillComputationBase[BrainSchema, ResultSchema],
    WithAsyncInvokeConfigVerified[
        ComputationRequested,
        ComputationResult[BrainSchema, ResultSchema]
    ],
    RunnableStreameable[
        ComputationRequested,
        ComputationResult[BrainSchema, ResultSchema]
    ],
    Generic[
        BrainSchema,
        ResultSchema,
    ]
):
    sub_type: Literal['direct'] = 'direct'

    @abstractmethod
    async def async_executor(
        self,
        skill_args: BrainSchema,
        config: BaseModel
    ) -> ResultSchema:
        """Ejecución del computo del skill

        Encargado de procesar los datos de entrada
        y generar el resultado.

        Returns:
            ResultSchema: resultado de ejecutar el computo
        """
        pass

    async def async_invoke_config_parsed(
        self,
        input: ComputationRequested,
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> ComputationResult[BrainSchema, ResultSchema]:
        callback_manager = get_callback_manager_for_config(config_raw)
        run_manager = callback_manager.on_chain_start(
            serialized=dumpd(self),
            inputs=input,
        )
        brain_args_payload = input.brain_args
        # Validamos que el payload cumpla con el modelo
        brain_args = self.brain_schema.model_validate(brain_args_payload)
        value = await self.async_executor(brain_args, config_parsed)
        result = ComputationResult[BrainSchema, ResultSchema](
            name=input.name,
            computation_id=input.computation_id,
            result=value,
            skill_args=brain_args
        )
        run_manager.on_chain_end(result)
        return result


class SkillComputationWithClarification(
    SkillComputationBase[BrainSchema, ResultSchema],
    WithAsyncInvokeConfigVerified[
        ComputationRequestedWithClarification,
        ComputationResult[BrainSchema, ResultSchema]
    ],
    RunnableStreameable[
        ComputationRequestedWithClarification,
        ComputationResult[BrainSchema, ResultSchema]
    ],
    Generic[
        BrainSchema,
        ClarificationSchema,
        SkillInputSchema,
        ResultSchema,
    ]
):
    sub_type: Literal['with-clarification'] = 'with-clarification'
    clarification_schema: Type[ClarificationSchema]
    skill_input_schema: Type[SkillInputSchema]

    @abstractmethod
    def merge_brain_with_clarification(
        self,
        brain_input: BrainSchema,
        clarification_input: ClarificationSchema,
    ) -> SkillInputSchema:
        ...

    @abstractmethod
    async def async_executor(
        self,
        skill_args: SkillInputSchema,
        config: BaseModel
    ) -> ResultSchema:
        """Ejecución del computo del skill

        Encargado de procesar los datos de entrada
        y generar el resultado.

        Returns:
            ResultSchema: resultado de ejecutar el computo
        """
        pass

    def get_clarification_schema(
        self, config: Optional[RunnableConfig] = None
    ) -> Type[ClarificationSchema]:
        return self.clarification_schema

    async def async_invoke_config_parsed(
        self,
        input: ComputationRequestedWithClarification,
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> ComputationResult[SkillInputSchema, ResultSchema]:
        callback_manager = get_callback_manager_for_config(config_raw)
        run_manager = callback_manager.on_chain_start(
            serialized=dumpd(self),
            inputs=input,
        )
        brain_args_payload = input.brain_args
        # Validamos que el payload cumpla con el esquema
        brain_args = self.brain_schema.model_validate(brain_args_payload)
        clarification_args_payload = input.clarification_args
        # Validamos que el payload cumpla con el esquema
        clarification_args = self.clarification_schema.model_validate(
            clarification_args_payload
        )
        computation_args = self.merge_brain_with_clarification(
            brain_args,
            clarification_args
        )
        value = await self.async_executor(computation_args, config_parsed)
        result = ComputationResult[SkillInputSchema, ResultSchema](
            name=input.name,
            computation_id=input.computation_id,
            result=value,
            skill_args=computation_args
        )
        run_manager.on_chain_end(result)
        return result


SkillComputation = Annotated[
    Union[
        SkillComputationDirect[BrainSchema, ResultSchema],
        SkillComputationWithClarification[
            BrainSchema, ClarificationSchema, SkillInputSchema, ResultSchema
        ]
    ],
    Field(discriminator='sub_type')
]


SkillComputationAdapter: TypeAdapter[SkillComputation] = TypeAdapter(
    Annotated[
        SkillComputation,
        Field(discriminator='sub_type')
    ]
)
