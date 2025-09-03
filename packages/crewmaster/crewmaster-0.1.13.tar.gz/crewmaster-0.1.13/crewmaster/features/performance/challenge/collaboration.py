
from datetime import datetime
from typing import (
    Dict,
    Literal,
    cast,
)
import structlog

from ...brain.brain_types import (
    BrainInput,
    BrainOutput,
    BrainInputFresh,
    BrainOutputContribution,
)
from ...collaborator.message import (
    UserMessage,
)
from ...skill import (
    Skill,
)
from .challenge_summary import (
    ChallengeSummary,
)
from .challenge_base import (
    ChallengePayloadBase,
    ChallengeBase,
)
from ..evaluator import (
    MatchEvaluator,
    IsInstanceEvaluator,
)
from ..score import (
    Score,
    ScoreBooleanDirect,
)


log = structlog.get_logger()
"Loger para el módulo"


class CollaborationChallengePayload(ChallengePayloadBase):
    user_name: str
    message_content: str
    message_to: str
    ideal: str


def create_message(content: str):
    return UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=content
    )


class CollaborationChallenge(
    ChallengeBase[
        CollaborationChallengePayload
    ]
):
    type: Literal[
        'performance.challenge.collaboration'
    ] = 'performance.challenge.collaboration'

    @property
    def summary(self) -> ChallengeSummary:
        summary = ChallengeSummary(
            idx=self.index,
            description=self.data.message_content[:40]
        )
        return summary

    def _build_brain_input(
        self
    ) -> BrainInput:
        # Extract fields from data
        data = self.data
        message_content = data.message_content
        user_name = data.user_name
        # Build brain input
        brain_input = BrainInputFresh(
            messages=[create_message(message_content)],
            user_name=user_name,
            today=datetime.now().isoformat()
        )
        return brain_input

    async def _run_fixed_evaluators(
        self,
        brain_output: BrainOutput,
        skills: Dict[str, Skill],
    ) -> Dict[str, ScoreBooleanDirect]:
        result = {
            "response_type": await IsInstanceEvaluator().evaluate(
                input=self.data.message_content,
                received=brain_output,
                expected=BrainOutputContribution,
                alias='response_type',
            )
        }
        if not result["response_type"].value:
            return result
        brain_contribution = cast(BrainOutputContribution, brain_output)
        result["recipient"] = await MatchEvaluator().evaluate(
                input=self.data.message_content,
                received=brain_contribution.message.to,
                expected=self.data.message_to,
                alias="recipient"
            )
        return result

    async def _run_dynamic_evaluators(
        self,
        brain_output: BrainOutput,
        skills: Dict[str, Skill],
    ) -> Dict[str, Score]:
        if not isinstance(brain_output, BrainOutputContribution):
            return {}
        received = str(brain_output.message.content)
        expected = self.data.ideal
        result: Dict[str, Score] = {
            evaluator.name: await evaluator.evaluate(
                input=self.data.message_content,
                received=received,
                expected=expected,
            )
            for evaluator in self.evaluators
        }
        return result
