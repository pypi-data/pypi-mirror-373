from typing import (
    List,
    Dict,
    Generic,
)
import structlog
from ...core.pydantic import (
    ConfigDict,
)

from langgraph.checkpoint.base import (
    BaseCheckpointSaver
)
from ..collaborator import (
    CollaboratorConfig,
    ClarificationContext,
    ClarificationRequested,
)
from ..skill import (
    BrainSchema,
)
from langchain_core.load.serializable import Serializable


log = structlog.get_logger()
"Loger para el módulo"


class CrewConfig(CollaboratorConfig):
    checkpointer: BaseCheckpointSaver

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ClarificationPending(
    Serializable,
    Generic[
        BrainSchema
    ]
):
    requested: ClarificationRequested
    context: ClarificationContext

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "requested": self.requested,
            "context": self.context
        }
