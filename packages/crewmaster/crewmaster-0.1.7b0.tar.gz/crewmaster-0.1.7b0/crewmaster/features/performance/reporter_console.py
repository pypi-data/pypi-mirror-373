import structlog

from .reporter_adapter_base import (
    ReporterAdapterBase,
    AptitudeSummary,
    ChallengeSummary,
    PerformanceReviewSummary,
)
from .score import (
    ScoreError,
)
from .challenge import (
    ChallengeResult
)
from .perforrmance_review_result import (
    PerformanceReviewResult
)
from .aptitude_base import AptitudeResult

log = structlog.get_logger()
"Loger para el módulo"


class ReporterConsole(ReporterAdapterBase):

    def start_performance(self, summary: PerformanceReviewSummary) -> None:
        log.info('')
        log.info('==================')
        log.info(f'Performance Review "{summary.name}"')
        log.info(
            f'Evaluando {summary.aptitudes} '
            f'aptitudes para {summary.agent_name}')
        log.info('-----------------')

    def start_aptitude(self, summary: AptitudeSummary) -> None:
        log.info(
            f'[ Aptitude {summary.name} '
            f'with {summary.challenges} challenges ]'
        )

    def start_challenge(self, summary: ChallengeSummary) -> None:
        log.info(f'* challenge[{summary.idx}] "{summary.description}"')

    def end_challenge(self, result: ChallengeResult) -> None:
        fixed = [
            f'{k} = '
            f'{s.value if not isinstance(s, ScoreError) else s.explanation}'
            for k, s in result.fixed_aspects.items()
        ]
        dynamic = [
            f'{s.name} = '
            f'{s.value if not isinstance(s, ScoreError) else s.explanation}'
            for s in result.dynamic_aspects.values()
        ]
        log.info(f'   fixed   [ {" | ".join(fixed)} ]')
        log.info(f'   dynamic [ {" | ".join(dynamic)} ]')
        log.info(f'*  score   = {result.score}')

    def end_aptitude(self, result: AptitudeResult) -> None:
        log.info(
            f'[ Aptitude score = {result.score} ]'
        )

    def end_performance(self, result: PerformanceReviewResult) -> None:
        log.info('-----------------')
        log.info(f'Performance Review score={result.global_score}')
        log.info('==================')
