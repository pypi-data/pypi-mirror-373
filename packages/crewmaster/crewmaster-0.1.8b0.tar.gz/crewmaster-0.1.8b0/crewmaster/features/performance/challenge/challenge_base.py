from abc import abstractmethod
from typing import (
    Dict,
    List,
    TypeVar,
    Generic,
)
import structlog
from ....core.pydantic import (
    BaseModel,
    model_validator,
)
from ..reporter_adapter_base import (
    ChallengeSummary,
)
from ..evaluator import (
    Evaluator,
)
from ..score import (
    Score,
)
from ...skill import (
    Skill,
)
from .challenge_result import (
    ChallengeResult,
)
from ..execution_context import (
    ExecutionContext
)
from ...brain.brain_types import (
    BrainInput,
    BrainOutput,
)


log = structlog.get_logger()
"Loger para el módulo"


class ChallengePayloadBase(BaseModel):
    ...


ChallengePayload = TypeVar('ChallengePayload', bound=ChallengePayloadBase)


class ChallengeBase(
    BaseModel,
    Generic[
        ChallengePayload
    ]
):
    index: int
    data: ChallengePayload
    evaluators: List[Evaluator]

    @model_validator(mode='before')
    def ensure_unique_evaluators(cls, values):
        evaluators = values.get("evaluators", [])
        # Convert to a set of serialized representations for uniqueness check
        serialized_evaluators = {e.get("name", "") for e in evaluators}
        if len(serialized_evaluators) != len(evaluators):
            raise ValueError("Evaluators must be unique.")
        return values

    @property
    @abstractmethod
    def summary(self) -> ChallengeSummary:
        ...

    @abstractmethod
    def _build_brain_input(
        self,
    ) -> BrainInput:
        ...

    @abstractmethod
    async def _run_fixed_evaluators(
        self,
        brain_output: BrainOutput,
        skills: Dict[str, Skill]
    ) -> Dict[str, Score]:
        ...

    @abstractmethod
    async def _run_dynamic_evaluators(
        self,
        brain_output: BrainOutput,
        skills: Dict[str, Skill]
    ) -> Dict[str, Score]:
        ...

    async def _calculate_score(
        self,
        fixed: Dict[str, Score],
        dynamic: Dict[str, Score]
    ) -> int:
        if len(fixed):
            score_fixed = sum(
                score.points for score in fixed.values()
            ) / len(fixed)
        else:
            score_fixed = 0  # Handle cases where there are no fixed_aspects
        if len(dynamic) > 0:
            score_dynamic = sum(
                score.points for score in dynamic.values()
            ) / len(dynamic)
        else:
            score_dynamic = None  # Indicate no dynamic_aspects
        # Determine the final score based on the conditions
        if score_dynamic is None:
            # Only fixed_aspects contribute
            score = int(score_fixed)
        else:
            # Average of score_fixed and score_dynamic
            score = int((score_fixed + score_dynamic) / 2)
        return score

    async def _evaluate(
        self,
        brain_output: BrainOutput,
        skills: Dict[str, Skill]
    ) -> ChallengeResult:
        fixed = await self._run_fixed_evaluators(
            brain_output=brain_output,
            skills=skills,
        )
        dynamic = await self._run_dynamic_evaluators(
            brain_output=brain_output,
            skills=skills,
        ) if len(self.evaluators) > 0 else {}
        score = await self._calculate_score(
            fixed=fixed,
            dynamic=dynamic
        )
        result = ChallengeResult(
            score=score,
            fixed_aspects=fixed,
            dynamic_aspects=dynamic
        )
        return result

    async def execute(
        self,
        context: ExecutionContext,
    ) -> ChallengeResult:
        reporter = context.reporter
        configuration = context.configuration
        reporter.start_challenge(self.summary)
        brain = context.brain
        # Convert challenge to brain input
        input = self._build_brain_input()
        # Call the brain (llm)
        result = brain.invoke(input, configuration)
        # Evaluate response from brain
        evaluation = await self._evaluate(
            brain_output=result,
            skills=brain.get_skills_as_dict()
        )
        # report result
        reporter.end_challenge(evaluation)
        return evaluation
