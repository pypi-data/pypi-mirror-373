from typing import Callable, Iterable
import uuid

import advanced_alchemy
from advanced_alchemy.service import SQLAlchemyAsyncQueryService
from msgspec import Struct
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth_core import check_password, generate_activate_code, hash_password, validate_activate_code
from ..models import AuthCodeModel, PermissionModel, UserModel, UserRoleAssociation
from ..repositories import (
    AuthCodeRepository,
    PermissionRepository,
    RolePermissionAssociationRepository,
    RoleRepository,
    UserRepository,
    UserRoleAssociationRepository,
)
from .exceptions import (
    ActivateUserNotFoundException,
    ActivateUserWrongCodeException,
    LoginUserNotFoundException,
    LoginWrongPasswordException,
    RegisterUserAlreadyExistsException,
    RegisterUserPasswordToShortException,
    ResetPasswordNotFoundException,
    ResetPasswordWrongCodeException,
    SetUserPasswordNotFoundException,
)

__all__ = (
    "AuthService",
    "provide_auth_service",
    "LoginRequest",
    "RegisterRequest",
    "ResetPasswordRequest",
    "StartResetPasswordRequest",
)

MIN_PASSWORD_LENGTH = 8


class LoginRequest(Struct):
    email: str
    password: str


class RegisterRequest(Struct):
    email: str
    password: str


class ResetPasswordRequest(Struct):
    code: str
    password: str


class StartResetPasswordRequest(Struct):
    email: str


class AuthService(SQLAlchemyAsyncQueryService):
    auth_code: AuthCodeModel

    def __init__(self, *args, emit_event: Callable[..., None], **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._role_repository = RoleRepository(session=self.repository.session)
        self._user_repository = UserRepository(session=self.repository.session)
        self._permission_repository = PermissionRepository(session=self.repository.session)

        self._user_role_association_repository = UserRoleAssociationRepository(session=self.repository.session)
        self._role_permission_repository = RolePermissionAssociationRepository(session=self.repository.session)

        self._auth_code_repository = AuthCodeRepository(session=self.repository.session)
        self.emit_event = emit_event

    async def login(self, data: LoginRequest) -> UserModel:
        try:
            login_user = await self._user_repository.get_one(UserModel.email == data.email)
        except advanced_alchemy.exceptions.NotFoundError:
            raise LoginUserNotFoundException(f"User with email {data.email} not found")

        if not check_password(
            data.password,
            login_user.password,
        ):
            raise LoginWrongPasswordException("Invalid password")

        if not login_user.is_active:
            # send code for activate user
            await self._send_auth_code(login_user)

        return login_user

    async def register(self, data: RegisterRequest) -> UserModel:
        email = data.email
        password = data.password
        exist_user = await self._user_repository.list(UserModel.email == email)

        if len(exist_user):
            raise RegisterUserAlreadyExistsException("User already exists")

        if len(data.password) < MIN_PASSWORD_LENGTH:
            raise RegisterUserPasswordToShortException("Password too short")

        register_user = await self._user_repository.add(
            UserModel(email=email, password=hash_password(password), is_active=False)
        )
        await self._user_repository.add_user_role(register_user, "customer")
        await self._send_auth_code(register_user)

        return register_user

    async def activate(self, code: str):
        try:
            self.auth_code = await self._auth_code_repository.get_one(AuthCodeModel.code == code)
        except advanced_alchemy.exceptions.NotFoundError:
            raise ActivateUserNotFoundException("code not found")

        if validate_activate_code(self.auth_code.code, str(self.auth_code.user_id)):
            await self._auth_code_repository.delete(self.auth_code.id)
            return await self._user_repository.activate(self.auth_code.user_id)
        else:
            raise ActivateUserWrongCodeException("code expired or wrong")

    async def start_reset_password(self, email: str):
        try:
            user = await self._user_repository.get_one(UserModel.email == email)
        except advanced_alchemy.exceptions.NotFoundError:
            raise ResetPasswordNotFoundException("user not found")

        await self._send_auth_code(user)

    async def reset_password(self, data: ResetPasswordRequest):
        try:
            auth_code = await self._auth_code_repository.get_one(AuthCodeModel.code == data.code)
        except advanced_alchemy.exceptions.NotFoundError:
            raise ResetPasswordNotFoundException("code not found")

        if validate_activate_code(auth_code.code, str(auth_code.user_id)):
            await self._auth_code_repository.delete(auth_code.id)

            # activate user on reset password
            await self._user_repository.activate(auth_code.user_id)
            return await self._user_repository.reset_password(auth_code.user_id, hash_password(data.password))
        else:
            raise ResetPasswordWrongCodeException("code expired or wrong")

    async def _send_auth_code(self, user: UserModel) -> None:
        try:
            self.auth_code = await self._auth_code_repository.get_one(AuthCodeModel.user_id == user.id)
            await self._auth_code_repository.update(
                AuthCodeModel(
                    id=self.auth_code.id,
                    code=str(generate_activate_code(str(user.id))),
                ),
                auto_commit=True,
            )
        except advanced_alchemy.exceptions.NotFoundError:
            self.auth_code = await self._auth_code_repository.add(
                AuthCodeModel(code=str(generate_activate_code(str(user.id))), user_id=user.id),
                auto_commit=True,
            )
        self.emit_event("send_auth_code", user.email, self.auth_code.code)

    async def update_user_roles(self, user_id: uuid.UUID, roles):
        exist_user_roles = await self._user_role_association_repository.list(UserRoleAssociation.user_id == user_id)
        exist_user_role_ids = {str(user_role.role_id) for user_role in exist_user_roles}
        next_user_role_ids = {role.get("id") for role in roles}

        await self._user_role_association_repository.delete_where(
            UserRoleAssociation.user_id == user_id,
            UserRoleAssociation.role_id.in_(exist_user_role_ids - next_user_role_ids),
        )
        await self._user_role_association_repository.add_many(
            UserRoleAssociation(user_id=user_id, role_id=uuid.UUID(role_id))
            for role_id in next_user_role_ids - exist_user_role_ids
        )

    async def update_role_permissions(self, role_id: uuid.UUID, permissions: Iterable[str | uuid.UUID]):
        role = await self._role_repository.get(role_id)
        role.permissions = await self._permission_repository.list(PermissionModel.id.in_(permissions))
        self.repository.session.add(role)
        await self.repository.session.commit()

    async def set_user_password(self, email: str, newpassword: str):
        try:
            user = await self._user_repository.get_one(UserModel.email == email)
        except advanced_alchemy.exceptions.NotFoundError:
            raise SetUserPasswordNotFoundException

        await self._user_repository.update(
            UserModel(
                id=user.id,
                password=hash_password(newpassword),
            ),
            auto_commit=True,
        )


async def provide_auth_service(db_session: AsyncSession, emit_event: Callable[..., None]) -> AuthService:
    return AuthService(session=db_session, emit_event=emit_event)
