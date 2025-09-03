from typing import Any, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token


from fastapi.security import APIKeyHeader
from fastapi import (
    Body,
    Depends,
    HTTPException,
)
from pydantic import (
    PrivateAttr,
)
import structlog

from .auth_strategy_interface import AuthStrategyInterface
from .user_logged import UserLogged


log = structlog.get_logger()
"Logger para la clase"


api_key_in_header = APIKeyHeader(
    name="Authorization",
    auto_error=False
)


def api_key_in_body(
    token: str = Body(None, embed=True)
):
    return token


def get_token_from_request(
    api_key_in_header: Optional[str] = Depends(api_key_in_header),
    api_key_in_body: Optional[str] = Depends(api_key_in_body)
):
    if api_key_in_header is not None:
        api_key_in_header = api_key_in_header.replace("Bearer ", "")
        return api_key_in_header
    if api_key_in_body is None:
        raise HTTPException(
            status_code=401,
            detail=(
                "Not authenticated.  Please provide a valid token in header"
            ),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key_in_body


def build_google_credentials(
    token_uri: str,
    client_id: str,
    client_secret: str,
):
    def _factory(
        self,
        refresh_token: str = Depends(get_token_from_request),
    ) -> Credentials:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret
        )
        return credentials
    return _factory


class GoogleAuthStrategy(AuthStrategyInterface):
    token_uri: str
    client_id: str
    client_secret: str

    _user_logged: Optional[UserLogged] = PrivateAttr(None)

    def _build_google_credentials(
        self,
        refresh_token: str,
    ) -> Credentials:
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=self.token_uri,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return credentials

    def _validate_credentials(
        self,
        credentials: Credentials
    ) -> dict[str, Any]:
        try:
            credentials.refresh(GoogleRequest())
            id_user_token = credentials.id_token
            user_info = id_token.verify_oauth2_token(
                id_user_token,
                GoogleRequest(),
                credentials.client_id,
                clock_skew_in_seconds=5
            )
            return user_info
        except Exception as error:
            raise HTTPException(
                status_code=401,
                detail=str(error),
                headers={"WWW-Authenticate": "Bearer"},
            )

    def current_user(self):
        return self._user_logged

    def execute(
        self,
        refresh_token: str = Depends(get_token_from_request)
    ):
        credentials = self._build_google_credentials(
            refresh_token=refresh_token
        )
        user_info = self._validate_credentials(credentials)
        email = user_info.get('email', 'unknown@sin.com')
        user_logged = UserLogged(
            email=email,
            credentials=credentials,
            name=None,
            timezone=None,
        )
        self._user_logged = user_logged
        return self._user_logged
