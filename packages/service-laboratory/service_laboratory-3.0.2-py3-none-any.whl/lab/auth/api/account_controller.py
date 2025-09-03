from typing import List
from uuid import UUID

from litestar import Request, get, post
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import HTTPException, NotAuthorizedException, NotFoundException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from pydantic import BaseModel, ConfigDict, SecretStr

from ..auth_core import encode_jwt_token
from ..auth_events import provide_emit_event
from ..models import UserModel
from ..repositories import provide_user_repository
from ..services import (
    ActivateUserNotFoundException,
    ActivateUserWrongCodeException,
    AuthService,
    LoginUserNotFoundException,
    LoginWrongPasswordException,
    RegisterUserAlreadyExistsException,
    RegisterUserPasswordToShortException,
    ResetPasswordNotFoundException,
    ResetPasswordRequest,
    ResetPasswordWrongCodeException,
    StartResetPasswordRequest,
    provide_auth_service,
)

MIN_PASSWORD_LENGTH = 8


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Role(Base):
    id: UUID | None
    name: str


class UserDetailResponse(Base):
    id: UUID | None
    email: str
    password: SecretStr
    roles: List[Role]
    is_enabled: bool
    is_active: bool


class RegisterRequest(BaseModel):
    email: str
    password: str


class ActivateRequest(BaseModel):
    code: str


class RegisterResponse(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user: UserDetailResponse


class StartResetPasswordResponse(BaseModel):
    message: str


class ActivateResponse(LoginResponse): ...


class ResetPasswordResponse(LoginResponse): ...


class AccountController(Controller):
    @staticmethod
    def generate_token(user_data: UserModel) -> str:
        user = UserDetailResponse.model_validate(user_data)
        return encode_jwt_token(user.model_dump(mode="json"))

    dependencies = {
        "user_repository": Provide(provide_user_repository),
        "auth_service": Provide(provide_auth_service),
        "emit_event": Provide(provide_emit_event),
    }
    path = "/account"

    @post(path="/login", exclude_from_auth=True)
    async def login(
        self,
        auth_service: AuthService,
        data: LoginRequest,
    ) -> LoginResponse:
        try:
            login_user = await auth_service.login(data)
        except LoginUserNotFoundException:
            raise NotFoundException(f"User with email {data.email} not found")
        except LoginWrongPasswordException:
            raise NotFoundException("Invalid password")

        access_token = self.generate_token(login_user)

        return LoginResponse(
            user=UserDetailResponse.model_validate(login_user),
            access_token=access_token,
        )

    @get(path="/me")
    async def me(
        self,
        request: Request,
    ) -> UserDetailResponse:
        if not request.user:
            raise NotAuthorizedException()
        return UserDetailResponse(**request.user)

    @post(path="/register", exclude_from_auth=True)
    async def register(
        self,
        auth_service: AuthService,
        data: RegisterRequest,
    ) -> RegisterResponse:
        try:
            await auth_service.register(data)
        except RegisterUserAlreadyExistsException:
            raise HTTPException("User already exists", status_code=HTTP_409_CONFLICT)
        except RegisterUserPasswordToShortException:
            raise HTTPException("Password too short", status_code=HTTP_400_BAD_REQUEST)

        return RegisterResponse(message="success")

    @post(path="/activate", exclude_from_auth=True)
    async def activate(
        self,
        auth_service: AuthService,
        data: ActivateRequest,
    ) -> ActivateResponse:
        try:
            activate_user = await auth_service.activate(data.code)

        except ActivateUserNotFoundException:
            raise HTTPException("Auth code not found", status_code=HTTP_404_NOT_FOUND)

        except ActivateUserWrongCodeException:
            raise HTTPException("Auth code wrong or expired", status_code=HTTP_400_BAD_REQUEST)

        return ActivateResponse(
            user=UserDetailResponse.model_validate(activate_user),
            access_token=self.generate_token(activate_user),
        )

    @post(path="/start-reset-password", exclude_from_auth=True)
    async def start_reset_password_request(
        self, auth_service: AuthService, data: StartResetPasswordRequest
    ) -> StartResetPasswordResponse:
        try:
            await auth_service.start_reset_password(data.email)
        except ResetPasswordNotFoundException:
            raise HTTPException("Email not found", status_code=HTTP_404_NOT_FOUND)

        return StartResetPasswordResponse(message="success")

    @post(path="/reset-password", exclude_from_auth=True)
    async def reset_password(
        self,
        auth_service: AuthService,
        data: ResetPasswordRequest,
    ) -> ResetPasswordResponse:
        try:
            user = await auth_service.reset_password(
                ResetPasswordRequest(
                    code=data.code,
                    password=data.password,
                )
            )
        except ResetPasswordNotFoundException:
            raise HTTPException("Auth code not found", status_code=HTTP_404_NOT_FOUND)

        except ResetPasswordWrongCodeException:
            raise HTTPException("Auth code wrong or expired", status_code=HTTP_400_BAD_REQUEST)

        return ResetPasswordResponse(
            user=UserDetailResponse.model_validate(user),
            access_token=self.generate_token(user),
        )
