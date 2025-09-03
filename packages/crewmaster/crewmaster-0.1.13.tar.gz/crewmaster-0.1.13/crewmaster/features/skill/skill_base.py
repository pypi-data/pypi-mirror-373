from typing import (
    Any,
    Dict,
    Generic,
    Type,
)
from ...core.pydantic import (
    BaseModel,
)
from langchain_core.utils.json_schema import dereference_refs
import structlog
from .types import (
    BrainSchema,
)

log = structlog.get_logger()
"Loger para el módulo"


class ToolModel(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class SkillBase(
    BaseModel,
    Generic[BrainSchema]
):
    name: str
    description: str
    brain_schema: Type[BrainSchema]

    def as_tool(self) -> Dict[str, Any]:
        return ToolModel(
            name=self.name,
            description=self.description,
            parameters=dereference_refs(self.brain_schema.model_json_schema())
        ).model_dump()
