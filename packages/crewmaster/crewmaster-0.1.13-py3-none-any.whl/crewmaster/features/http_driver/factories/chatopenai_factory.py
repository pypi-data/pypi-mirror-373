from langchain_openai import ChatOpenAI
import structlog
from ....core.pydantic import (
    SecretStr,
)


log = structlog.get_logger()
"Loger para el módulo"


def chatopenai_factory(
    api_key: str,
    model: str,
    temperature: float,
):
    service = ChatOpenAI(
        api_key=SecretStr(api_key),
        model=model,
        temperature=temperature
    )
    return service
