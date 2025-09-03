from datetime import datetime
from typing import (
    Any,
    Dict,
    List,
    Literal,
    cast,
)
import structlog
from ....core.pydantic import (
    BaseModel,
)
from ...brain.brain_types import (
    BrainInput,
    BrainOutput,
    BrainInputFresh,
    BrainOutputComputationsRequired,
)
from ...collaborator.message import (
    UserMessage,
)
from ..evaluator import (
    IsInstanceEvaluator,
    SubSetEvaluator,
    PydanticModelChecker,
    PydanticModelEquality,
)
from ..score import (
    Score,
    ScoreError,
    ScoreBooleanDirect,
    ScorePercentDirect,
)
from ...skill import (
    Skill,
    ComputationRequested,
)
from .challenge_base import (
    ChallengePayloadBase,
    ChallengeBase,
)
from .challenge_summary import (
    ChallengeSummary,
)


log = structlog.get_logger()
"Loger para el módulo"


class ExpectedSkill(BaseModel):
    name: str
    arguments: Dict[str, Any]


class SkillSelectionChallengePayload(ChallengePayloadBase):
    expected_skills: List[ExpectedSkill]
    message_content: str
    user_name: str


def create_message(content: str):
    return UserMessage(
        id='1222',
        timestamp=datetime.now().isoformat(),
        content=content
    )


class SkillSelectionChallenge(
    ChallengeBase[
        SkillSelectionChallengePayload
    ]
):
    type: Literal[
        'performance.challenge.skill_selection'
    ] = 'performance.challenge.skill_selection'

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

    async def _evaluate_args_structure(
        self,
        computation: ComputationRequested,
        skill: Skill
    ) -> ScoreBooleanDirect:
        evaluator = PydanticModelChecker(
            model=skill.brain_schema
        )
        evaluation = await evaluator.evaluate(
            alias=f'{skill.name}-structure',
            input='',
            expected=None,
            received=computation.brain_args
        )
        return evaluation

    async def _evaluate_args_equality(
        self,
        computation: ComputationRequested,
        skill: Skill,
        expected_skill: ExpectedSkill
    ) -> ScoreBooleanDirect:
        evaluator = PydanticModelEquality(
            model=skill.brain_schema
        )
        evaluation = await evaluator.evaluate(
            alias=f'{skill.name}-equality',
            input='',
            expected=expected_skill.arguments,
            received=computation.brain_args
        )
        return evaluation

    async def _run_fixed_evaluators(
        self,
        brain_output: BrainOutput,
        skills: Dict[str, Skill],
    ) -> Dict[str, Score]:
        # Validamos que los expected_skills se correspondan
        # con los skills que posee el brain
        expected_names = [exp.name for exp
                          in self.data.expected_skills]
        skills_in_agent = [name for name in skills.keys()]
        is_subset = set(expected_names).issubset(set(skills_in_agent))
        if not is_subset:
            return {
                "expected_skills": ScoreError(
                    name='expected_skills',
                    explanation='skills expected are not available in agent',
                    source=(
                        f'expected:{expected_names}, '
                        f'availables: {skills_in_agent}'
                    )
                )
            }

        result: Dict[str, Score] = {
            "response_type": await IsInstanceEvaluator().evaluate(
                input=self.data.message_content,
                received=brain_output,
                expected=BrainOutputComputationsRequired,
                alias='response_type',
            )
        }
        if isinstance(
            result["response_type"], ScoreBooleanDirect
        ) and not result["response_type"].value:
            return result
        brain_contribution = cast(
            BrainOutputComputationsRequired,
            brain_output
        )
        received_names = [skill.name for skill
                          in brain_contribution.computations_required]
        expected_names = [exp.name for exp
                          in self.data.expected_skills]
        result["skills_selected"] = await SubSetEvaluator().evaluate(
                input=self.data.message_content,
                received=received_names,
                expected=expected_names,
                alias="skills_selected"
        )
        received_computations = {skill.name: skill for skill
                                 in brain_contribution.computations_required
                                 if skill.name in expected_names}
        expected_skills = {expected.name: expected
                           for expected in self.data.expected_skills}

        evaluation_structure = {name: await self._evaluate_args_structure(
                                    request,
                                    skills[request.name]
                                )
                                for name, request
                                in received_computations.items()}
        structure_value = sum(score.points
                              for score in evaluation_structure.values())
        result['skills_structure'] = ScorePercentDirect(
            name='skills_structure',
            explanation=str(evaluation_structure),
            value=structure_value
        )
        evaluation_equality = {
            request.name: await self._evaluate_args_equality(
                request,
                skills[request.name],
                expected_skills[name]
            )
            for name, request
            in received_computations.items()
        }
        equality_value = sum(score.points
                             for score in evaluation_equality.values())
        result['skills_equality'] = ScorePercentDirect(
            name='skills_equality',
            explanation=str(evaluation_equality),
            value=equality_value
        )
        return result

    async def _run_dynamic_evaluators(
        self,
        brain_output: BrainOutput,
        skills: Dict[str, Skill]
    ) -> Dict[str, Score]:
        if not isinstance(brain_output, BrainOutputComputationsRequired):
            return {}
        return {}
        # received = str(brain_output.message.content)
        # expected = self.data.ideal
        # result: Dict[str, Score] = {
        #     evaluator.name: await evaluator.evaluate(
        #         input=self.data.message_content,
        #         received=received,
        #         expected=expected,
        #     )
        #     for evaluator in self.evaluators
        # }
        # return result
