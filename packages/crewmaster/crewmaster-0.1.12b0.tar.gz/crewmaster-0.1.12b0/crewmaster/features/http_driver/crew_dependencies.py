from typing import (
    Any,
)
from pydantic import (
    BaseModel as BaseModelV2,
)

from .auth import (
    UserLogged,
)


class CrewDependencies(BaseModelV2):
    checkpointer: Any
    llm_srv: Any
    user_logged: UserLogged
    user_name: str
    today: str
