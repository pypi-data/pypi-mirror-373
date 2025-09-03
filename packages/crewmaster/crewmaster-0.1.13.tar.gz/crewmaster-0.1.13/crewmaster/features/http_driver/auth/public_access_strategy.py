import structlog
from pydantic import (
    PrivateAttr,
)
from .auth_strategy_interface import AuthStrategyInterface
from .user_logged import UserLogged

log = structlog.get_logger()
"Logger para la clase"


class PublicAccessStrategy(AuthStrategyInterface):

    _user_logged: UserLogged = PrivateAttr(
        UserLogged(
            email="anonymous@unknown.com",
            name="anonymous",
            timezone=None,
            credentials=None
        )
    )

    def execute(
        self
    ):
        return self._user_logged

    def current_user(
        self
    ):
        return self._user_logged
