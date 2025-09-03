from typing import (
    Optional,
    Any,
)
from pydantic import (
    BaseModel as BaseModelV2
)


class UserLogged(BaseModelV2):
    email: str
    name: Optional[str]
    timezone: Optional[str]
    credentials: Any
