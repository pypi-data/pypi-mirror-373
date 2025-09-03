from typing import (
    TypeVar,
)
import structlog

from ...core.pydantic import (
    BaseModel,
)
from langchain_core.runnables import (
    RunnableSerializable,
)


log = structlog.get_logger()
"Loger para el módulo"


Input = TypeVar('Input', bound=BaseModel)
Output = TypeVar('Output', bound=BaseModel)
"""Tipos genéricos para la clase RunnableStremeable"""


class RunnableStreameable(
    RunnableSerializable[Input, Output]
):
    pass
