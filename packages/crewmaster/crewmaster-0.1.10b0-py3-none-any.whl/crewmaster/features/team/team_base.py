from typing import (
    List,
    cast
)
import structlog
from ...core.pydantic import (
    PrivateAttr,
    BaseModel,
)

from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.runnables.config import (
    merge_configs,
)
from langchain_core.runnables.utils import (
    get_unique_config_specs,
)
from langgraph.graph import (
    StateGraph
)
from langgraph.graph.graph import CompiledGraph
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)


from ..collaborator import (
    ClarificationMessage,
    CollaboratorBase,
    CollaboratorInputClarification,
    CollaboratorInputFresh,
    CollaboratorOutputClarification,
    CollaboratorOutputContribution,
    CollaboratorOutputResponse,
    CollaboratorOutputResponseStructured,
    CollaboratorState,
    Colleague,
    TeamMembership,
    UserMessage,
)
from ..skill import (
    SkillContribute,
    Skill,
)
from ..agent.agent_base import AgentBase

from .distribution_strategy import (
    DistributionStrategyInterface,
)


log = structlog.get_logger()
"Loger para el módulo"


def start(
    state: CollaboratorState,
    config: RunnableConfig
):
    pass


def distributor(
    default_agent: str,
):
    def executor(
        state: CollaboratorState,
        config: RunnableConfig
    ):
        # Evaluamos si hay nueva contribución
        output = state.output
        if isinstance(output, CollaboratorOutputContribution):
            target = output.contribution.to
            return {
                "output": None,
                "next_step": f'run_{target}'
            }
        fresh = state.fresh_message
        if isinstance(fresh, ClarificationMessage):
            target = fresh.to
            return {'next_step': f'run_{target}'}
        # Si no tiene destinatario lo enviamos al default_agent
        return {'next_step': f'run_{default_agent}'}
    return executor


def evaluate_distributor(
    state: CollaboratorState,
    config: RunnableConfig
):
    return state.next_step


def agent_node(
    agent: AgentBase
):
    async def executor(
        state: CollaboratorState,
        config: RunnableConfig
    ):
        fresh = state.fresh_message
        if isinstance(fresh, UserMessage):
            agent_input = CollaboratorInputFresh(
                public_messages=state.public_messages,
                private_messages=state.private_messages,
                message=fresh
            )
        elif isinstance(fresh, ClarificationMessage):
            agent_input = CollaboratorInputClarification(
                public_messages=state.public_messages,
                private_messages=state.private_messages,
                clarification_message=fresh
            )
        else:
            raise ValueError('Unknown fresh_message for agent')
        default_config = RunnableConfig(
            run_name="cbr:agent",
            tags=["cbr:agent"],
            metadata={"cbr_agent_name": agent.name}
        )
        config_tunned = merge_configs(default_config, config)
        result = await agent.ainvoke(agent_input, config_tunned)
        return {
            "output": result
        }

    return executor


def router(
    state: CollaboratorState,
    config: RunnableConfig
):
    output = state.output
    if isinstance(output, (
        CollaboratorOutputResponse,
        CollaboratorOutputResponseStructured,
        CollaboratorOutputClarification,
    )):
        return {"next_step": "response_ready"}
    if isinstance(output, CollaboratorOutputContribution):
        return {"next_step": "contribution"}
    raise ValueError('Unknown agent outupt response type')


def evaluate_router(
    state: CollaboratorState,
    config: RunnableConfig
):
    return state.next_step


def collaborator(
    state: CollaboratorState,
    config: RunnableConfig
):
    # Si alguien hace una contribución debemos agregarlo
    # a la lista de mensajes privados
    output = state.output
    if not isinstance(output, CollaboratorOutputContribution):
        raise ValueError(
            'Collaborator only handle CollaboratorOutputContribution'
        )
    output = cast(CollaboratorOutputContribution, output)
    message = output.contribution

    return {
        "private_messages": state.private_messages + [message]
    }


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


class TeamBase(CollaboratorBase):
    name: str = 'Team'
    job_description: str
    team_instructions: str = (
        'You are part of a team of colleagues.'
        'Please use tool if you need to send a message to anyone.\n\n'
        'Members:\n'
    )
    distribution_strategy: DistributionStrategyInterface
    members: List[AgentBase]
    _graph: CompiledGraph = PrivateAttr()
    options_built_in: List[Skill] = []

    def __init__(
        self,
        **data
    ):
        super().__init__(**data)
        self._notify_members()

    def _notify_members(self):
        membership = TeamMembership(
            name=self.name,
            members=[
                Colleague(
                    name=member.name,
                    job_description=member.job_description
                ) for member in self.members
            ],
            instructions=self.team_instructions,
            collaboration_tools=[SkillContribute()]
        )
        for member in self.members:
            member.join_team(membership)

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        team = super().config_specs
        agent_config_specs = [spec for agent in self.members
                              for spec in agent.config_specs]
        combined = agent_config_specs + team
        return get_unique_config_specs(combined)

    def _build_graph(
        self,
        graph: StateGraph,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
    ) -> StateGraph:
        # Agregamos los nodos al graph
        graph.add_node(start)               # type: ignore
        default_agent = self.distribution_strategy.execute()
        graph.add_node('distributor', distributor(
            default_agent=default_agent.name
        ))         # type: ignore
        for member in self.members:
            graph.add_node(
                node=member.name,
                action=agent_node(member)   # type: ignore
            )
        graph.add_node(router)              # type: ignore
        graph.add_node(collaborator)        # type: ignore
        graph.add_node(cleaner)             # type: ignore
        # Establecemos el punto de entrada
        graph.set_entry_point('start')
        # Agregamos los bordes
        graph.add_edge('start', 'distributor')
        graph.add_conditional_edges(
            source='distributor',
            path=evaluate_distributor,
            path_map={f'run_{agent.name}': agent.name
                      for agent in self.members}
        )
        for member in self.members:
            graph.add_edge(
                start_key=member.name,
                end_key='router'
            )
        graph.add_conditional_edges(
            source='router',
            path=evaluate_router,
            path_map={
                "response_ready": 'cleaner',
                "contribution": "collaborator"
            }
        )
        graph.add_edge(
            start_key='collaborator',
            end_key='distributor'
        )
        # Establecemos el punto de finalización
        graph.set_finish_point('cleaner')
        # Compilamos el grafo
        return graph

    def join_team(
        self,
        team_membership: TeamMembership
    ):
        self.team_membership = team_membership
        for member in self.members:
            member.join_team(
                team_membership=team_membership
            )
        self.options_built_in += team_membership.collaboration_tools

    def get_member_by_name(
        self,
        agent_name: str
    ) -> AgentBase:
        filtered = [member for member in self.members
                    if member.name == agent_name]
        if len(filtered) < 1:
            raise ValueError(f'Agent "{agent_name}" dont exist in team')
        return filtered[0]
