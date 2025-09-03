from typing import (
    Any,
    TypeVar,
    Union,
    Dict,
    Generic,
    List,
)
from ...core.pydantic import (
    BaseModel,
    computed_field,
)
from functools import cached_property

import structlog
from langchain_core.load.serializable import Serializable


log = structlog.get_logger()
"Loger para el módulo"


class BrainSchemaBase(BaseModel):
    @computed_field()
    @cached_property
    def registry_id(self) -> str:
        return self.__class__.__name__


class ClarificationSchemaBase(BaseModel):
    ...


class SkillInputSchemaBase(BaseModel):
    ...


class ResultSchemaBase(BaseModel):
    ...


BrainSchema = TypeVar(
    'BrainSchema',
    bound=BrainSchemaBase
)
ClarificationSchema = TypeVar(
    'ClarificationSchema',
    bound=ClarificationSchemaBase
)
SkillInputSchema = TypeVar(
    'SkillInputSchema',
    bound=Union[BrainSchemaBase, SkillInputSchemaBase]
)
ResultSchema = TypeVar(
    'ResultSchema',
    bound=ResultSchemaBase
)
"""Tipos genéricos para la clase Computation"""


def get_all_subclasses(cls):
    """Get subclasses"""
    for subclass in cls.__subclasses__():
        yield from get_all_subclasses(subclass)
        yield subclass


class ComputationRequested(
    Serializable
):
    name: str
    brain_args: Dict[str, Any]
    # brain_args: AnyBrain
    computation_id: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "name": self.name,
            "brain_args": self.brain_args,
            "computation_id": self.computation_id
        }

    @classmethod
    def lc_id(cls) -> list[str]:
        """A unique identifier for this class for serialization purposes.

        The unique identifier is a list of strings that describes the path
        to the object.
        For example, for the class `langchain.llms.openai.OpenAI`, the id is
        ["langchain", "llms", "openai", "OpenAI"].
        """
        # Pydantic generics change the class name.
        # So we need to do the following
        if (
            "origin" in cls.__pydantic_generic_metadata__
            and cls.__pydantic_generic_metadata__["origin"] is not None
        ):
            original_name = cls.__pydantic_generic_metadata__[
                "origin"
            ].__name__
        else:
            original_name = cls.__name__
        return [*cls.get_lc_namespace(), original_name]


class ComputationRequestedWithClarification(
    Serializable
):
    name: str
    brain_args: Dict[str, Any]
    clarification_args: Dict[str, Any]
    computation_id: str

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "name": self.name,
            "brain_args": self.brain_args,
            "clarification_args": self.clarification_args,
            "computation_id": self.computation_id
        }

    @classmethod
    def lc_id(cls) -> list[str]:
        """A unique identifier for this class for serialization purposes.

        The unique identifier is a list of strings that describes the path
        to the object.
        For example, for the class `langchain.llms.openai.OpenAI`, the id is
        ["langchain", "llms", "openai", "OpenAI"].
        """
        # Pydantic generics change the class name.
        # So we need to do the following
        if (
            "origin" in cls.__pydantic_generic_metadata__
            and cls.__pydantic_generic_metadata__["origin"] is not None
        ):
            original_name = cls.__pydantic_generic_metadata__[
                "origin"
            ].__name__
        else:
            original_name = cls.__name__
        return [*cls.get_lc_namespace(), original_name]


class ComputationResult(
    Serializable,
    Generic[
        SkillInputSchema,
        ResultSchema
    ],
):
    computation_id: str
    name: str
    skill_args: SkillInputSchema
    result: ResultSchema

    @classmethod
    def is_lc_serializable(cls) -> bool:
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        return cls.__module__.split(".")

    @property
    def lc_attributes(self) -> Dict:
        return {
            "computation_id": self.computation_id,
            "name": self.name,
            "skill_args": self.skill_args,
            "result": self.result,
        }
