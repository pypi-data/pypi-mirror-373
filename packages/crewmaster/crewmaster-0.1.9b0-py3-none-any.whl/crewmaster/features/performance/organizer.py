import structlog

from .organizer_base import (
    OrganizerBase,
)
from .performance_review import (
    PerformanceReview,
)

log = structlog.get_logger()
"Loger para el módulo"


class Organizer(OrganizerBase):

    def organize(
        self,
        name: str,
        subject: str,
    ) -> PerformanceReview:

        aptitudes = self.loader.load_aptitudes(
            llm_judge=self.llm_judge
        )

        result = PerformanceReview(
            name=name,
            agent_name=subject,
            team=self.team,
            aptitudes=aptitudes,
            reporter=self.reporter
        )
        return result
