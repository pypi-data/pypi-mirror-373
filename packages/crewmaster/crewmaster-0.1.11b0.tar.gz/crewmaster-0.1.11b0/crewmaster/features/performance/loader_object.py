from typing import (
    Any,
    Dict,
    List,
    Optional,
)
import structlog
from langchain_core.language_models import (
    BaseLanguageModel,
)
from .loader_strategy_base import (
    LoaderStrategyBase,
)
from .aptitude import (
    Aptitude,
    AptitudeAdapter,
)


log = structlog.get_logger()
"Loger para el módulo"


ChallengeRaw = Dict[str, Any]


class LoaderObject(LoaderStrategyBase):
    collaboration: List[
        ChallengeRaw
    ] = []
    skill_selection: List[
        ChallengeRaw
    ] = []
    skill_interpretation: List[
        ChallengeRaw
    ] = []
    free_response: List[
        ChallengeRaw
    ] = []
    structured_response: List[
        ChallengeRaw
    ] = []

    def _build_evaluators(
        self,
        challenge_raw: ChallengeRaw,
        llm_judge: Optional[BaseLanguageModel]
    ) -> List[Dict[str, Any]]:
        evaluators_names = challenge_raw.get("evaluators", [])
        evaluators = [{"name": name, "llm_judge": llm_judge}
                      for name in evaluators_names]
        return evaluators

    def _add_metadata(
        self,
        type: str,
        list_raw: List[ChallengeRaw],
        llm_judge: Optional[BaseLanguageModel]
    ) -> List[ChallengeRaw]:
        with_index = [
                {
                    "data": {**challenge},
                    "index": i,
                    "type": type,
                    "evaluators": self._build_evaluators(
                        challenge,
                        llm_judge=llm_judge
                    )
                }
                for i, challenge in enumerate(list_raw)
        ]
        return with_index

    def _load_aptitude(
        self,
        alias: str,
        raw_challenges: List[Dict[str, Any]],
        llm_judge: Optional[BaseLanguageModel],
    ) -> Optional[Aptitude]:
        if not raw_challenges:
            return None
        challenge_type = f'performance.challenge.{alias}'
        aptitude_type = f'performance.aptitude.{alias}'
        challenges_with_metadata = self._add_metadata(
            challenge_type,
            raw_challenges,
            llm_judge=llm_judge
        )
        return AptitudeAdapter.validate_python({
            "type": aptitude_type,
            "challenges": challenges_with_metadata
        })

    def load_aptitudes(
        self,
        llm_judge: Optional[BaseLanguageModel]
    ) -> List[Aptitude]:
        # Map challenges to their respective Challenge and Aptitude classes
        aptitude_mapping = [
            (
                'collaboration',
                self.collaboration,
            ),
            (
                'skill_selection',
                self.skill_selection,
            ),
            (
                'skill_interpretation',
                self.skill_interpretation,
            ),
            (
                'free_response',
                self.free_response,
            ),
            (
                'structured_response',
                self.structured_response,
            ),
        ]

        aptitudes = [
            self._load_aptitude(name, data, llm_judge=llm_judge)
            for name, data in aptitude_mapping
        ]

        return [aptitude for aptitude in aptitudes if aptitude is not None]
