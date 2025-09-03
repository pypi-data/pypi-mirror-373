from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    cast,
)
from ...core.pydantic import (
    model_validator,
    BaseModel,
)
from langchain_core.utils.aiter import aclosing

import structlog
from langchain_openai import ChatOpenAI
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain.agents.output_parsers.openai_tools import (
    OpenAIToolsAgentOutputParser
)
from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    BaseMessage,
    AIMessageChunk,
)
from langchain_core.runnables.utils import (
    ConfigurableFieldSpec
)
from langchain_core.agents import (
    AgentFinish,
    AgentAction,
)
from langchain_core.prompt_values import (
    PromptValue,
)
from langchain.agents.output_parsers.tools import (
    ToolAgentAction
)
from langchain_core.messages.tool import (
    ToolCall
)
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.callbacks.manager import (
    CallbackManagerForChainRun
)
from ..runnables import (
    WithInvokeConfigVerified,
    WithAsyncStreamConfigVerified,
    RunnableStreameable,
)
from ..helpers import (
    check_templates_for_valid_placeholders
)
from ..collaborator import (
    AgentMessage,
    HistoryStrategyInterface,
    MaxMessagesStrategy,
    TokenUsage,
)
from ..skill import (
    ComputationRequested,
    ComputationResult,
    Skill,
    SkillStructuredResponse,
)
from .brain_types import (
    BrainInput,
    BrainInputBase,
    BrainInputResults,
    BrainOutput,
    BrainOutputComputationsRequired,
    BrainOutputContribution,
    BrainOutputResponse,
    BrainOutputResponseStructured,
    InstructionsTransformerFn,
    SituationBuilderFn,
)


log = structlog.get_logger()
"Loger para el módulo"


def ensure_dict(
    candidate: str | Dict[str, Any],
    key: str = 'input'
) -> Dict[str, Any]:
    if isinstance(candidate, str):
        candidate = {key: candidate}
    return candidate


def convert_action_to_computation(
    action: AgentAction
) -> ComputationRequested:
    tool_call_id = action.tool_call_id if (
        isinstance(action, ToolAgentAction)
     ) else ''
    tool_input = action.tool_input if (
                    isinstance(action.tool_input, Dict)
                ) else {"value": action.tool_input}
    result = ComputationRequested(
        name=action.tool,
        computation_id=tool_call_id,
        brain_args=tool_input
    )
    return result


def is_response_structured(
    name: str,
    skills: List[Skill]
):
    """Checks if an Skill with the given
       name is of type 'response_structured'.

    Args:
        name: The name of the Skill to check.
        skills: A list of Skill instances.

    Returns:
        True if an Skill with the given name
        and type 'response_structured' exists, False otherwise.
    """
    return any(
        skill.name == name and
        isinstance(skill, SkillStructuredResponse)
        for skill in skills
    )


def convert_to_tool_message(
    value: ComputationResult
) -> ToolMessage:
    converted = ToolMessage(
        name=value.name,
        tool_call_id=value.computation_id,
        content=str(value.result)
    )
    return converted


def convert_to_tool_call(
    value: ComputationResult
) -> ToolCall:
    result = ToolCall(
        name=value.name,
        args=value.skill_args.model_dump(),
        id=value.computation_id
    )
    return result


class BrainBase(
    WithInvokeConfigVerified[BrainInput, BrainOutput],
    WithAsyncStreamConfigVerified[BrainInput, BrainOutput],
    RunnableStreameable[BrainInput, BrainOutput]
):
    name: str = "brain"
    instructions: str
    agent_name: str
    situation_builder: Optional[SituationBuilderFn] = None

    skills: List[Skill] = []
    history_strategy: HistoryStrategyInterface = MaxMessagesStrategy()
    instructions_transformer: Optional[InstructionsTransformerFn] = None

    @property
    def config_specs(self) -> List[ConfigurableFieldSpec]:
        """List configurable fields for this runnable."""
        return [
            ConfigurableFieldSpec(
                id='llm_srv',
                name='LLM para consultar',
                description=(
                    'Servicio para conectarse con un LLM provider,'
                ),
                annotation=ChatOpenAI,
                default=...
            )
        ]

    @model_validator(mode='before')
    def validate_templates(cls, values):
        templates_properties = [
            'instructions'
        ]
        brain_input_fields = BrainInputBase.model_fields.keys()
        return check_templates_for_valid_placeholders(
            source=values,
            properties_using_templates=templates_properties,
            availables_keys=brain_input_fields
        )

    def _build_messages_for_llm(
        self,
        input: BrainInput,
        config: RunnableConfig,
    ) -> PromptValue:
        situation = ''
        if self.situation_builder is not None:
            situation = self.situation_builder(input, config)

        instructions_with_situation = self.instructions + situation
        if self.instructions_transformer is not None:
            instructions_with_situation = self.instructions_transformer(
                instructions_with_situation,
                input,
                config
            )
        system_message = SystemMessagePromptTemplate.from_template(
            instructions_with_situation
        )

        history = input.messages
        history_summary = self.history_strategy.execute(history)

        # Buscamos los mensajes de tool para pasarlos como Mensajes al LLM
        computation_messages = []
        if isinstance(input, BrainInputResults):
            results = input.computations_results
            tools_messages = [convert_to_tool_message(result)
                              for result in results]
            tools_calls = [convert_to_tool_call(result)
                           for result in results]
            tool_request = AIMessage(
                tool_calls=tools_calls,
                content=''
            )
            computation_messages = [tool_request] + tools_messages

        context = ChatPromptTemplate.from_messages(
            [system_message] + history_summary + computation_messages
        )
        input_as_dict = dict(input)
        result = context.invoke(input_as_dict, config)
        return result

    def _parse_actions(
        self,
        message: BaseMessage
    ) -> BrainOutput:
        usage = message.usage_metadata if (
                            isinstance(message, AIMessage)
                        ) else None
        token_usage = TokenUsage.model_validate(
                                    usage
                                ) if usage is not None else None
        actions_or_finish = OpenAIToolsAgentOutputParser().invoke(message)
        if isinstance(actions_or_finish, AgentFinish):
            finish = actions_or_finish
            message = AgentMessage(
                content=finish.return_values.get('output', ''),
                to='user',
                author=self.agent_name
            )
            result = BrainOutputResponse(
                message=message,
                token_usage=token_usage
            )
            return result

        actions = actions_or_finish
        contributions = [action for action in actions
                         if action.tool == 'send_message_to_colleague']
        if len(contributions) > 0:
            contribution_tool = contributions[0]
            if isinstance(contribution_tool.tool_input, str):
                raise ValueError('Invalid tool_input for Contribution')
            contribution_input = contribution_tool.tool_input or {}
            content = contribution_input.get("message", "")
            to = contribution_input.get("to", "")
            message = AgentMessage(
                content=content,
                to=to,
                author=self.agent_name
            )
            return BrainOutputContribution(
                message=message,
                token_usage=token_usage
            )

        structured = [action for action in actions
                      if is_response_structured(action.tool, self.skills)]
        if len(structured) > 0:
            response = cast(ToolAgentAction, structured[0])
            tool_input = ensure_dict(response.tool_input)
            return BrainOutputResponseStructured(
                payload=tool_input,
                structure=response.tool,
                message_id=response.tool_call_id,
                token_usage=token_usage
            )
        computations = [convert_action_to_computation(action)
                        for action in actions]
        return BrainOutputComputationsRequired(
            computations_required=computations,
            token_usage=token_usage
        )

    def _setup_llm(
        self,
        config_parsed: BaseModel,
    ):
        configurable = getattr(config_parsed, "configurable")
        llm_srv = cast(ChatOpenAI, getattr(configurable, "llm_srv"))
        tools = [skill.as_tool() for skill in self.skills]
        llm_with_tools = llm_srv.bind_tools(tools)
        return llm_with_tools

    def invoke_config_parsed(
        self,
        input: BrainInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig
    ) -> BrainOutput:
        # configuramos el llm con los tools
        llm_with_tools = self._setup_llm(config_parsed=config_parsed)
        # Construimos los mensajes que se van a enviar al LLM
        messages_to_llm = self._build_messages_for_llm(input, config_raw)
        # Ejecutamos el llm
        result_llm = llm_with_tools.invoke(messages_to_llm, config_raw)
        # Transformamos el resultado
        result = self._parse_actions(result_llm)
        return result

    async def astream_config_parsed(
        self,
        input: BrainInput,
        config_parsed: BaseModel,
        config_raw: RunnableConfig,
        run_manager: CallbackManagerForChainRun,
        **kwargs: Optional[Any],
    ) -> AsyncIterator[BaseMessage]:
        # configuramos el llm con los tools
        llm_with_tools = self._setup_llm(config_parsed=config_parsed)
        # Construimos los mensajes que se van a enviar al LLM
        messages_to_llm = self._build_messages_for_llm(input, config_raw)
        iterator = llm_with_tools.astream(
            messages_to_llm,
            config_raw,
        )
        complete_response: BaseMessage = AIMessageChunk(content='')
        async with aclosing(iterator):
            async for chunk in iterator:
                complete_response += chunk
                yield chunk
        result = self._parse_actions(complete_response)
        run_manager.on_chain_end(result)

    def get_skills_as_dict(
        self
    ) -> Dict[str, Skill]:
        skills = self.skills
        skill_map: Dict[
            str, Skill
        ] = {skill.name: skill
             for skill in skills}
        return skill_map
