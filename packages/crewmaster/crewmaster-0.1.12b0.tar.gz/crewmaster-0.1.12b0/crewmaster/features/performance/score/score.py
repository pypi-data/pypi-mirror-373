from typing import (
    Annotated,
    Literal,
    Union,
    Any,
    List,
)
import structlog
from ....core.pydantic import (
    Field,
    TypeAdapter,
    StringConstraints,
)
from .score_base import (
    ScoreBase,
    Percent,
)


log = structlog.get_logger()
"Loger para el módulo"


class ScorePercent(ScoreBase):
    type: Literal[
        'performance.challenge.score.percent'
    ] = 'performance.challenge.score.percent'
    value: int = Field(ge=0, le=100)


class ScorePercentDirect(ScorePercent):
    @property
    def points(self) -> Percent:
        return self.value


class ScorePercentInverse(ScorePercent):
    @property
    def points(self) -> Percent:
        return 100 - self.value


class ScoreBoolean(ScoreBase):
    type: Literal[
        'performance.challenge.score.boolean'
    ] = 'performance.challenge.score.boolean'
    value: bool


class ScoreBooleanDirect(ScoreBoolean):
    @property
    def points(self) -> Percent:
        return 100 if self.value else 0


class ScoreBooleanInverse(ScoreBoolean):
    @property
    def points(self) -> Percent:
        return 0 if self.value else 100


CategoryName = Annotated[
    str,
    StringConstraints(
        max_length=25,
        min_length=3,
        to_upper=True
    )
]


class ScoreCategorical(ScoreBase):
    type: Literal[
        'performance.challenge.score.categorical'
    ] = 'performance.challenge.score.categorical'
    value: List[CategoryName]
    max_categories_allowed: int = Field(ge=1, le=10)


class ScoreCategoricalDirect(ScoreCategorical):
    @property
    def points(self) -> Percent:
        points_x_category = int(100/self.max_categories_allowed)
        return len(self.value) * points_x_category


class ScoreCategorialInverse(ScoreCategorical):
    @property
    def points(self) -> Percent:
        points_x_category = int(100/self.max_categories_allowed)
        total_points = len(self.value) * points_x_category
        return 100 - total_points


class ScoreCategoricalBinary(ScoreCategorical):
    max_categories_allowed: int = 1
    correct_categories: List[CategoryName]

    @property
    def points(self) -> Percent:
        result = 100 if (
            self.value[0].upper() in self.correct_categories
        ) else 0
        return result


class ScoreError(ScoreBase):
    type: Literal[
        'performance.challenge.score.error'
    ] = 'performance.challenge.score.error'
    source: Any

    @property
    def points(self) -> Percent:
        return 0


Score = Union[
    ScorePercent,
    ScoreBoolean,
    ScoreCategorical,
    ScoreError,
]

ScoreAdapter: TypeAdapter[Score] = TypeAdapter(
    Annotated[
        Score,
        Field(discriminator='type')
    ]
)
