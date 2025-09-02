from typing import (
    Callable,
    Dict,
    Generic,
    List,
    Type,
    TypeVar,
    TypedDict,
    Union,
)
from ...ultra_result.either import (
    Either
)
from .emitter import (
    Emitter,
)

LeftType = TypeVar('LeftType')
RightType = TypeVar('RightType')


class NaturalResponse(TypedDict, Generic[LeftType, RightType]):
    explanation: str
    result: Either[LeftType, RightType]


class EmitterExplained(
    Generic[LeftType, RightType],
    Emitter[NaturalResponse[LeftType, RightType]]
):
    right_explanation_fn: Union[
        Callable[[RightType], str],
        str
    ]
    left_exclusive: Dict[Type[Exception], str] = {}
    left_multiple_intro: str = 'Can not process because {count} problems: '

    def __init__(
        self,
        right_explanation_fn:  Union[
            Callable[[RightType], str],
            str
        ],
        left_exclusive: Dict[Type[Exception], str] = {},
        left_multiple_intro: str = 'Can not process because {count} problems: '
    ):
        self.right_explanation_fn = right_explanation_fn
        self.left_exclusive = left_exclusive
        self.left_multiple_intro = left_multiple_intro

    def _build_left_explanation(
        self,
        errors: List[LeftType]
    ) -> str:
        if len(errors) == 1:
            specials = [value for key, value in self.left_exclusive.items()
                        if isinstance(errors[0], key)]
            if len(specials) > 0:
                return specials[0]
        errors_str = [f'"{str(item)}"' for item in errors]
        joined = ", ".join(errors_str)
        intro = self.left_multiple_intro.format(count=len(errors))
        explanation = f'{intro}{joined}'
        return explanation

    def _build_right_explanation(
        self,
        result: RightType
    ) -> str:
        if isinstance(self.right_explanation_fn, str):
            # If it's a string, return it directly
            return self.right_explanation_fn
        elif callable(self.right_explanation_fn):
            # If it's a callable, call it with the result and return the result
            return self.right_explanation_fn(result)
        else:
            raise ValueError("Invalid type for right_explanation_fn")

    def emit_value(
        self,
        result: Either[LeftType, RightType]
    ) -> None:
        if result.is_right():
            explanation = self._build_right_explanation(
                result.get_value()
            )
        else:
            explanation = self._build_left_explanation(
                result.get_errors()
            )
        full_response: NaturalResponse = {
            "explanation": explanation,
            "result": result
        }
        super().emit_value(full_response)
