import structlog
from langchain_core.runnables import (
    RunnableConfig,
)
from ...core.pydantic import (
    BaseModel,
)
from ..brain.brain_base import (
    BrainBase
)
from .reporter_adapter_base import (
    ReporterAdapterBase
)

log = structlog.get_logger()
"Loger para el módulo"


class ExecutionContext(BaseModel):
    brain: BrainBase
    configuration: RunnableConfig
    reporter: ReporterAdapterBase
