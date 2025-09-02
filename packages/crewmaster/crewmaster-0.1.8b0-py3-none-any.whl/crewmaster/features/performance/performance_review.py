from datetime import datetime
import structlog
from langchain_core.runnables import (
    RunnableConfig,
)
from .performance_review_base import (
    PerformanceReviewBase,
)
from .perforrmance_review_result import (
    PerformanceReviewResult
)
from .execution_context import (
    ExecutionContext,
)

log = structlog.get_logger()
"Loger para el módulo"


class PerformanceReview(PerformanceReviewBase):
    async def execute(
        self,
        configuration: RunnableConfig
    ) -> PerformanceReviewResult:
        self.reporter.start_performance(self.summary)
        agent = self.team.get_member_by_name(self.agent_name)
        brain = agent._brain

        context = ExecutionContext(
            brain=brain,
            reporter=self.reporter,
            configuration=configuration
        )
        results = {aptitude.type: await aptitude.execute(
                        context=context
                    )
                   for aptitude in self.aptitudes}
        # Extraemos los scores individuales
        scores = [result.score for result in results.values()]
        # calculamos el score del aptitude
        score = sum(scores) / len(scores) if scores else 0
        result = PerformanceReviewResult(
            date=datetime.now(),
            result=results,
            global_score=int(score),
            version='',
            name=self.name
        )
        self.reporter.end_performance(result=result)
        return result
