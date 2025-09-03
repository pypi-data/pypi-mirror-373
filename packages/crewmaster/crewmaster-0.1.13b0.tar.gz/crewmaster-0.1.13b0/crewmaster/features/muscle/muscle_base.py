from typing import (
    List,
    Optional,
)
import structlog
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from ...core.pydantic import (
    BaseModel,
)
from langchain_core.runnables.config import (
    get_callback_manager_for_config,
)
from langchain_core.load.dump import dumpd
from langchain_core.runnables.config import (
    merge_configs,
)
from ..collaborator import (
    ClarificationContext,
    ClarificationRequested,
)
from ..skill import (
    ComputationRequested,
    ComputationRequestedWithClarification,
    ComputationResult,
    SkillComputation,
    SkillComputationDirect,
    SkillComputationWithClarification,
)
from .muscle_types import (
    MuscleInput,
    MuscleInputClarificationResponse,
    MuscleInputComputationRequested,
    MuscleOutput,
    MuscleOutputResults,
    MuscleOutputClarification,
)
from ..runnables import (
    WithAsyncInvokeConfigVerified,
    RunnableStreameable,
)

log = structlog.get_logger()
"Loger para el módulo"


async def execute_computation(
    option: SkillComputationDirect | SkillComputationWithClarification,
    request: ComputationRequested | ComputationRequestedWithClarification,
    config: RunnableConfig,
) -> ComputationResult:
    default_config = RunnableConfig(
        tags=['cbr:skill']
    )
    config_tunned = merge_configs(default_config, config)
    if isinstance(
        option, SkillComputationDirect
    ) and isinstance(request, ComputationRequested):
        result = await option.ainvoke(
            input=request,
            config=config_tunned
        )
    elif isinstance(
        option, SkillComputationWithClarification
    ) and isinstance(request, ComputationRequestedWithClarification):
        result = await option.ainvoke(
            input=request,
            config=config_tunned
        )
    else:
        raise ValueError(
            'option must be a SkillComputationDirect '
            'or SkillComputationWithClarification instance'
        )
    return result


async def execute_computations_pending(
    pending: List[ComputationRequested],
    results: List[ComputationResult],
    options: List[SkillComputation],
    agent_name: str,
    config: RunnableConfig
) -> MuscleOutput:
    if pending is None or len(pending) == 0:
        return MuscleOutputResults(
            computations_requested=[],
            computations_results=results
        )
    # Buscamos si alguna opcion requiere clarification
    map_options = {option.name: option for option in options}
    clarifications = [job for job in pending
                      # if map_options[job.name].require_clarification]
                      if isinstance(
                          map_options[job.name],
                          SkillComputationWithClarification
                      )]
    if len(clarifications) > 0:
        computation = clarifications[0]
        clarification = ClarificationRequested(
            name=computation.name,
            clarification_id=computation.computation_id,
            brain_args=computation.brain_args
        )
        context = ClarificationContext(
            computations_requested=pending,
            computations_results=results,
            requested_by=agent_name
        )
        response = MuscleOutputClarification(
            clarification_requested=clarification,
            clarification_context=context
        )
        return response
    # Si llegamos aquí sólo hay computaciones directas
    requested = pending
    direct_results = [await execute_computation(
        option=map_options[job.name],
        request=job,
        config=config
    ) for job in requested]
    all_results = direct_results + results
    return MuscleOutputResults(
        computations_requested=[],
        computations_results=all_results
    )


async def process_computations_request(
    options: List[SkillComputation],
    input: MuscleInputComputationRequested,
    config: RunnableConfig,
    agent_name: str,
) -> MuscleOutput:
    pending = input.computations_required
    results = []
    return await execute_computations_pending(
        pending=pending,
        results=results,
        options=options,
        agent_name=agent_name,
        config=config
    )


async def process_clarification_response(
    options: List[SkillComputation],
    input: MuscleInputClarificationResponse,
    config: RunnableConfig,
    agent_name: str,
) -> MuscleOutput:
    message = input.clarification_message
    context = message.clarification_context
    requested = context.computations_requested
    results = context.computations_results
    # Buscamos que exista la clarification
    expected = [job for job in requested
                if (
                    job.computation_id == message.computation_id
                )]
    if len(expected) == 0:
        raise ValueError('Clarification received is not expected')
    clarification_request = expected[0]
    # Buscamos el skill asociado
    skill_list = [option for option in options
                  if option.name == clarification_request.name
                  and isinstance(
                      option, SkillComputationWithClarification
                    )
                  ]
    if len(skill_list) != 1:
        raise ValueError('Skill not found for clarification')
    computation_requested = ComputationRequestedWithClarification(
        name=clarification_request.name,
        brain_args=clarification_request.brain_args,
        clarification_args=message.payload,
        computation_id=clarification_request.computation_id
    )
    options_availables = [option for option in options
                          if option.name == clarification_request.name]
    if len(options_availables) == 0:
        raise ValueError(
            'No definition available for execute'
            f'{clarification_request.name}'
        )
    option_clarified = options_availables[0]
    computation_result = await execute_computation(
        option=option_clarified,
        request=computation_requested,
        config=config
    )
    # Sacamos la clarificación ejecutada de requested
    new_pending = [job for job in requested
                   if job.computation_id != message.computation_id]
    # Pasamos la clarificación ejecutada a results
    new_results = results + [computation_result]
    # Llamamos a process_computations para el resto
    result = await execute_computations_pending(
        pending=new_pending,
        results=new_results,
        options=options,
        agent_name=agent_name,
        config=config
    )
    return result


class MuscleBase(
    WithAsyncInvokeConfigVerified[
        MuscleInput, MuscleOutput
    ],
    RunnableStreameable[
        MuscleInput,
        MuscleOutput
    ],
):
    name: Optional[str] = 'cbr:muscle'
    agent_name: str
    options: List[SkillComputation] = []

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        """List configurable fields for this runnable."""
        # Construimos la lista a partir de las opciones
        # con que está trabajando el muscle
        options_specs = list({spec for option in self.options
                              for spec in option.config_specs})
        return options_specs

    def invoke(
        self,
        input: MuscleInput,
        config: RunnableConfig | None = None
    ) -> MuscleOutput:
        raise Exception('Muscle can only be invoked asynchronously')

    async def async_invoke_config_parsed(
            self,
            input: MuscleInput,
            config_parsed: BaseModel,
            config_raw: RunnableConfig
    ) -> MuscleOutput:
        callback_manager = get_callback_manager_for_config(config_raw)
        run_manager = callback_manager.on_chain_start(
            serialized=dumpd(self),
            inputs=input,
            name=self.name
        )

        if isinstance(input, MuscleInputComputationRequested):
            result = await process_computations_request(
                options=self.options,
                input=input,
                config=config_raw,
                agent_name=self.agent_name
            )
            run_manager.on_chain_end(result)
            return result
        if isinstance(input, MuscleInputClarificationResponse):
            result = await process_clarification_response(
                options=self.options,
                input=input,
                config=config_raw,
                agent_name=self.agent_name
            )
            run_manager.on_chain_end(result)
            return result
        raise ValueError(
            'Invalid type for Muscle'
        )
