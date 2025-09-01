from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidSignatureError,
)
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult
from litestar.middleware.base import DefineMiddleware

from .auth_core import decode_jwt_token

API_KEY_HEADER = "Authorization"
TOKEN_PREFIX = "Bearer "


class JWTAuthenticationMiddleware(AbstractAuthenticationMiddleware):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def authenticate_request(
        self,
        connection: ASGIConnection,
    ) -> AuthenticationResult:
        token = connection.headers.get(API_KEY_HEADER)

        if not token:
            raise NotAuthorizedException()

        token = token.replace(
            TOKEN_PREFIX,
            "",
        )
        try:
            token = decode_jwt_token(token)
        except (
            InvalidSignatureError,
            ExpiredSignatureError,
            InvalidAlgorithmError,
            DecodeError,
        ):
            raise NotAuthorizedException()

        user = token.payload
        if not user:
            raise NotAuthorizedException()
        return AuthenticationResult(
            user=user,
            auth=token,
        )


auth_middleware = DefineMiddleware(
    JWTAuthenticationMiddleware,
    exclude="/docs",
)
