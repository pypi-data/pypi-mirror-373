from typing import (
    Type,
    Literal,
)
import structlog


from .skill_base import (
    SkillBase,
)
from .types import (
    BrainSchemaBase
)


log = structlog.get_logger()
"Loger para el módulo"


class SendContribution(BrainSchemaBase):
    to: str
    message: str


class SkillContribute(
    SkillBase[SendContribution]
):
    type: Literal['skill.forward'] = 'skill.forward'
    name: str = 'send_message_to_colleague'
    description: str = 'Send a message to a colleague'
    brain_schema: Type[SendContribution] = SendContribution
