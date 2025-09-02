from typing import (
    Any,
    Dict,
    List,
)
from ...core.pydantic import (
    BaseModel,
    Field,
    SerializeAsAny,
)
import structlog

from langchain_openai import ChatOpenAI
from langchain_core.load.serializable import Serializable

from ..skill import (
    ComputationRequested,
    ComputationResult,
)

log = structlog.get_logger()
"Loger para el módulo"


class ClarificationContext(
    Serializable,
):
    computations_requested: List[
        SerializeAsAny[ComputationRequested]   # [BrainSchemaBase]
    ]
    computations_results: List[
        ComputationResult
    ]
    requested_by: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "computations_requested": self.computations_requested,
            "computations_results": self.computations_results,
            "requested_by": self.requested_by,
        }


class ClarificationRequested(
    Serializable,
    BaseModel
):
    # def model_dump(
    #   self, serialize_as_any = True,
    #   **kwargs
    # ) -> Dict[str, Any]:
    #     return super().model_dump(serialize_as_any=True, **kwargs)

    # def model_dump_json(self, serialize_as_any = True, **kwargs) -> str:
    #     return super().model_dump_json(serialize_as_any=True, **kwargs)

    name: str
    clarification_id: str
    brain_args: Dict[str, Any]

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "name": self.name,
            "clarification_id": self.clarification_id,
            "brain_args": self.brain_args,
        }


class CollaboratorConfig(BaseModel):
    llm_srv: ChatOpenAI
    use_cases_srv: Any
    user_name: str = Field(...)
    today: str


class Colleague(BaseModel):
    name: str
    job_description: str


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
