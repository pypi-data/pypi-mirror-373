from abc import abstractmethod
from typing import (
    Optional,
)
import structlog
from ...core.pydantic import (
    BaseModel,
)
from langchain_core.runnables import (
    RunnableConfig,
)
from langchain_core.language_models import (
    BaseLanguageModel,
)
from .performance_review_base import (
    PerformanceReviewBase,
)
from ..team import (
    TeamBase
)
from .loader_strategy_base import (
    LoaderStrategyBase
)
from .reporter_adapter_base import (
    ReporterAdapterBase,
)
from .reporter_console import (
    ReporterConsole
)

log = structlog.get_logger()
"Loger para el módulo"


class OrganizerBase(BaseModel):
    team: TeamBase
    loader: LoaderStrategyBase
    reporter: ReporterAdapterBase = ReporterConsole()
    llm_judge: Optional[BaseLanguageModel] = None

    @abstractmethod
    def organize(
        self,
        name: str,
        subject: str,
        config_runtime: RunnableConfig
    ) -> PerformanceReviewBase:
        ...
