import base64
from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt
from pydantic import BaseModel
import pyotp

from ..settings import settings

DEFAULT_TIME_DELTA = timedelta(days=30)
DEFAULT_OTP_INTERVAL = 60 * 10
ALGORITHM = "HS256"


class Token(BaseModel):
    exp: datetime
    sub: str
    payload: Any


def decode_jwt_token(
    token: str,
) -> Token:
    return Token(
        **jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
    )


def encode_jwt_token(
    payload,
    expiration: timedelta = DEFAULT_TIME_DELTA,
) -> str:
    token = Token(
        exp=datetime.now() + expiration,
        sub="auth",
        payload=payload,
    )
    return jwt.encode(
        {
            "exp": token.exp,
            "sub": token.sub,
            "payload": token.payload,
        },
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def hash_password(
    password: str,
) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def check_password(
    password: str,
    hashed_password: str,
) -> bool:
    try:
        if bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        ):
            return True
    except ValueError:
        return False

    return False


def _get_base32_string(user_uuid: str):
    return base64.b32encode(str(user_uuid).encode("utf-8")).decode("utf-8")


def generate_activate_code(user_uuid: str):
    otp = pyotp.TOTP(_get_base32_string(user_uuid + settings.otp_secret), digits=8, interval=DEFAULT_OTP_INTERVAL)
    return otp.now()


def validate_activate_code(code: str, user_uuid: str) -> bool:
    otp = pyotp.TOTP(_get_base32_string(user_uuid + settings.otp_secret), digits=8, interval=DEFAULT_OTP_INTERVAL)
    return otp.verify(code)
