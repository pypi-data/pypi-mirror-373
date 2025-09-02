from typing import (
    Any,
)
import structlog

from langchain_core.runnables import (
    RunnableLambda,
)


log = structlog.get_logger()
"Loger para el módulo"


def tap(label: str):
    def tap(
        input: Any,
        config: Any
    ):
        log.info(label, i=input)
        return input
    return RunnableLambda(tap)
