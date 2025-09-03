from abc import abstractmethod
from typing import (
    List,
    Optional,
)

import structlog
from langchain_core.language_models import (
    BaseLanguageModel,
)
from ...core.pydantic import (
    BaseModel,
)
from .aptitude import (
    Aptitude,
)

log = structlog.get_logger()
"Loger para el módulo"


class LoaderStrategyBase(BaseModel):

    @abstractmethod
    def load_aptitudes(
        self,
        llm_judge: Optional[BaseLanguageModel]
    ) -> List[Aptitude]:
        ...
