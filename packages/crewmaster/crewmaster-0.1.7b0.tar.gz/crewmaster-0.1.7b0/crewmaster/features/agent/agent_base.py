from itertools import groupby
from typing import (
    List,
    Optional,
    cast,
)
from ...core.pydantic import (
    PrivateAttr,
    BaseModel,
)
import structlog

from langgraph.graph.state import (
    StateGraph,
    CompiledStateGraph,
)
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.config import (
    merge_configs,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec,
)
from ..helpers import (
    snake_to_camel,
    create_dynamic_protocol,
)


from ..brain.brain_types import (
    BrainInputFresh,
    BrainInputResults,
    BrainOutputComputationsRequired,
    BrainOutputResponse,
    BrainOutputResponseStructured,
    BrainOutputContribution,
    SituationBuilderFn,
    InstructionsTransformerFn,
)
from ..muscle.muscle_types import (
    MuscleInputClarificationResponse,
    MuscleInputComputationRequested,
    MuscleOutputClarification,
    MuscleOutputResults,
)
from ..muscle.muscle_base import (
    MuscleBase
)
from ..brain.brain_base import (
    BrainBase,
)

from ..collaborator import (
    AgentMessage,
    AnyMessage,
    ClarificationMessage,
    CollaboratorBase,
    CollaboratorOutputClarification,
    CollaboratorOutputContribution,
    CollaboratorOutputResponse,
    CollaboratorOutputResponseStructured,
    CollaboratorState,
    HistoryStrategyInterface,
    MaxMessagesStrategy,
    TeamMembership,
    UserMessage,
)
from ..skill import (
    Skill,
    SkillComputationDirect,
    SkillComputationWithClarification,
)

log = structlog.get_logger()
"Loger para el módulo"


def start(
    state: CollaboratorState,
    config: RunnableConfig
):
    last_message = state.fresh_message
    next_step = 'fresh_message'
    if isinstance(last_message, ClarificationMessage):
        next_step = 'clarification_response'
    return {"next_step": next_step}


def evaluate_input(
    state: CollaboratorState,
    config: RunnableConfig
):
    return state.next_step


def brain_node(
    brain: BrainBase
):
    def executor(
        state: CollaboratorState,
        config: RunnableConfig
    ):
        fresh_message = state.fresh_message
        if not isinstance(fresh_message, (UserMessage, ClarificationMessage)):
            raise ValueError(
                'Brain only handle fresh or clarification message'
            )
        messages = (
            state.public_messages +
            state.private_messages +
            [fresh_message]
        )
        messages = cast(List[AnyMessage], messages)
        if len(state.computations_results) > 0:
            brain_input = BrainInputResults(
                messages=messages,
                user_name=config.get('configurable', {}).get('user_name', ''),
                today=config.get('configurable', {}).get('today', ''),
                computations_requested=state.computations_requested,
                computations_results=state.computations_results,
            )
        else:
            brain_input = BrainInputFresh(
                messages=messages,
                user_name=config.get('configurable', {}).get('user_name', ''),
                today=config.get('configurable', {}).get('today', ''),
            )
        default_config = RunnableConfig(
            run_name="cbr:brain",
            tags=['cbr:brain']
        )
        config_tunned = merge_configs(default_config, config)
        result = brain.invoke(
            input=brain_input,
            config=config_tunned
        )
        if isinstance(
            result, (BrainOutputResponse)
        ):
            output = CollaboratorOutputResponse(
                message=result.message
            )
            return {
                "next_step": "response_ready",
                "output": output
            }
        if isinstance(
            result, (BrainOutputResponseStructured)
        ):
            output = CollaboratorOutputResponseStructured(
                structure=result.structure,
                payload=result.payload,
                message=AgentMessage(
                    author=brain.agent_name,
                    to="User",
                    content=str(result.payload)
                )
            )
            return {
                "next_step": "response_ready",
                "output": output
            }
        if isinstance(
            result, (BrainOutputContribution)
        ):
            output = CollaboratorOutputContribution(
                contribution=result.message
            )
            return {
                "next_step": "response_ready",
                "output": output
            }
        if isinstance(
            result, (BrainOutputComputationsRequired)
        ):
            return {
                "next_step": "computations_requested",
                "computations_requested": result.computations_required
            }
        raise ValueError('Unkonwn Brain Output Type')
    return executor


def evaluate_brain(
    state: CollaboratorState,
    config: RunnableConfig
):
    return state.next_step


def muscle_node(
    muscle: MuscleBase
):
    async def executor(
        state: CollaboratorState,
        config: RunnableConfig
    ):
        fresh = state.fresh_message
        if isinstance(fresh, ClarificationMessage):
            muscle_input = MuscleInputClarificationResponse(
                clarification_message=fresh
            )
        else:
            computations_requested = state.computations_requested
            muscle_input = MuscleInputComputationRequested(
                computations_required=computations_requested
            )
        default_config = RunnableConfig(
            run_name="cbr:muscle",
            tags=['cbr:muscle']
        )
        config_tunned = merge_configs(default_config, config)
        # Ejecutamos el muscle
        result = await muscle.ainvoke(muscle_input, config_tunned)
        if isinstance(result, MuscleOutputClarification):
            # TODO: Falta preparar la clarificacion de salidaç
            context = result.clarification_context
            output = CollaboratorOutputClarification(
                clarification_context=context,
                clarification_requested=result.clarification_requested
            )
            return {
                "next_step": 'clarification_needed',
                "output": output,
                "computations_requested": context.computations_requested,
                "computations_results": context.computations_results
            }
        if isinstance(result, MuscleOutputResults):
            return {
                "next_step": 'computations_ready',
                "computations_requested": result.computations_requested,
                "computations_results": result.computations_results
            }
        raise ValueError(
            'Invalid result from muscle'
        )
    return executor


def evaluate_muscle(
    state: CollaboratorState,
    config: RunnableConfig
):
    return state.next_step


def cleaner(
    state: CollaboratorState,
    config: RunnableConfig
):
    """
    Nodo final del graph, se utiliza para cualquier limpieza
    que se quiera hacer al final del graph.

    Actualmente no se realiza ninguna operación,
    ya que en el estado se encuentra la variable output
    que se devuelve como resultado de la ejecución.
    """
    pass


class AgentBase(CollaboratorBase):
    name: str = 'agent'
    job_description: str

    agent_name_intro: str = (
        "Your name is "
    )
    public_bio: Optional[str] = None
    private_bio: Optional[str] = None
    directives: Optional[str] = None
    examples: Optional[str] = None
    team_membership: Optional[TeamMembership] = None
    options: List[Skill] = []
    options_built_in: List[Skill] = []
    history_strategy: HistoryStrategyInterface = MaxMessagesStrategy()
    situation_builder: Optional[SituationBuilderFn] = None
    instructions_transformer: Optional[InstructionsTransformerFn] = None

    _brain: BrainBase = PrivateAttr()
    _muscle: MuscleBase = PrivateAttr()
    _graph: CompiledStateGraph = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        instructions = self._build_instructions()
        all_options = self.options + self.options_built_in
        self._brain = BrainBase(
            agent_name=self.name,
            instructions=instructions,
            skills=all_options,
            history_strategy=self.history_strategy,
            situation_builder=self.situation_builder,
            instructions_transformer=self.instructions_transformer
        )
        computations = [opt for opt in all_options
                        if isinstance(
                            opt,
                            (SkillComputationDirect,
                             SkillComputationWithClarification)
                        )]
        self._muscle = MuscleBase(
            options=computations,
            agent_name=self.name
        )

    def _build_team_instructions(self) -> str | None:
        membership = self.team_membership
        team_instructions = None
        if membership is not None:
            team_instructions = membership.instructions
            list = [f'{member.name}: {member.job_description}'
                    for member in membership.members
                    if member.name != self.name]
            team_instructions += '\n'.join(list)
        return team_instructions

    def _build_instructions(self) -> str:
        team_instructions = self._build_team_instructions()
        your_name = f'{self.agent_name_intro} {self.name}' if (
            self.agent_name_intro is not None
        ) else None
        parts = [
            your_name,
            self.public_bio,
            self.private_bio,
            self.directives,
            self.job_description,
            team_instructions,
            self.examples
        ]
        template_total = "\n".join(filter(None, parts))
        return template_total

    def _merge_dependencies(
        self,
        deps: List[ConfigurableFieldSpec]
    ) -> List[ConfigurableFieldSpec]:
        # Group ConfigurableFieldSpec by id
        grouped = {
            spec_id: list(specs)
            for spec_id, specs in groupby(
                sorted(deps, key=lambda x: x.id), key=lambda x: x.id
            )
        }
        # Merge the dependencies
        merged = [
            # Creamos una clase dinámica
            # si hay varias interfaces con el mismo id
            ConfigurableFieldSpec(
                id=spec_id,
                name=f'Protocol for {spec_id}',
                description=(
                    'Protocol builded with all the members of required'
                    ' services from multiple runnables'
                ),
                default=...,
                annotation=create_dynamic_protocol(
                    f'{snake_to_camel(spec_id)}Protocol',
                    *[spec.annotation for spec in specs]
                )
            )
            if len(specs) > 1
            # Directly use the original ConfigurableFieldSpecif
            # only one annotation
            else specs[0]
            for spec_id, specs in grouped.items()
        ]
        return merged

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        team = super().config_specs
        all_options = self.options + self.options_built_in
        computations = [option for option in all_options
                        if isinstance(
                            option,
                            (SkillComputationDirect,
                             SkillComputationWithClarification)
                        )]
        options_config_specs = [spec for option in computations
                                for spec in option.config_specs
                                if isinstance(
                                    option,
                                    (SkillComputationDirect,
                                     SkillComputationWithClarification)
                                )]
        combined_specs = options_config_specs + team
        merged_deps = self._merge_dependencies(combined_specs)
        return merged_deps

    def join_team(
        self,
        team_membership: TeamMembership
    ):
        self.team_membership = team_membership
        instructions = self._build_instructions()
        all_options = (
            self.options +
            self.options_built_in +
            team_membership.collaboration_tools
        )
        self._brain = BrainBase(
            agent_name=self.name,
            instructions=instructions,
            skills=all_options,
            history_strategy=self.history_strategy
        )

    def _build_graph(
        self,
        graph: StateGraph,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
    ) -> StateGraph:
        # Agregamos los nodos
        graph.add_node(start)     # type: ignore
        graph.add_node('brain', brain_node(self._brain))     # type: ignore
        graph.add_node('muscle', muscle_node(self._muscle))    # type: ignore
        graph.add_node(cleaner)   # type: ignore
        # Defimos punto de entrada
        graph.set_entry_point('start')
        # Agregamos los bordes
        graph.add_conditional_edges(
            source='start',
            path=evaluate_input,
            path_map={
                "fresh_message": "brain",
                "clarification_response": "muscle"
            }
        )
        graph.add_conditional_edges(
            source='brain',
            path=evaluate_brain,
            path_map={
                "computations_requested": "muscle",
                "response_ready": "cleaner"
            }
        )
        graph.add_conditional_edges(
            source='muscle',
            path=evaluate_muscle,
            path_map={
                "clarification_needed": "cleaner",
                "computations_ready": "brain"
            }
        )
        # Agregamos el punto de salida
        graph.set_finish_point('cleaner')
        return graph
