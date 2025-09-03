import pytest
from sqlalchemy.ext.asyncio.session import AsyncSession
import time_machine

from ..auth_core import validate_activate_code
from ..models import AuthCodeModel, PermissionModel, RoleModel, UserModel
from ..services import (
    PermissionService,
    RegisterUserAlreadyExistsException,
    RegisterUserPasswordToShortException,
    ResetPasswordNotFoundException,
    RoleService,
    SetUserPasswordNotFoundException,
)
from ..services.auth_service import (
    AuthService,
    LoginRequest,
    LoginUserNotFoundException,
    LoginWrongPasswordException,
    RegisterRequest,
    ResetPasswordRequest,
    ResetPasswordWrongCodeException,
)


async def test_create_user(db_session: AsyncSession, user_service):
    user_data = UserModel(
        email="some3@email.com",
        password="super_password",
    )
    user_data = await user_service.create(user_data, auto_commit=True)
    user = await user_service.get(user_data.id)
    assert user.email == user_data.email

    # teardown
    await user_service.delete(user_data.id)


async def test_get_users(db_session, auth_fixtures, user_service):
    users = await user_service.list()
    assert len(users) == 7


async def test_get_roles(db_session, auth_fixtures, role_service):
    roles = await role_service.list()
    assert len(roles) == 4


async def test_get_permissions(db_session, auth_fixtures, permission_service):
    permissions = await permission_service.list()
    assert len(permissions) == 12


async def test_remove_permissions(db_session, auth_fixtures, permission_service, user_service):
    permissions = await permission_service.list()
    first_permission = permissions[0]
    await permission_service.delete(first_permission.id)

    permissions = await permission_service.list()
    assert len(permissions) == 11

    # teardown
    await permission_service.create(
        PermissionModel(
            app=first_permission.app,
            name=first_permission.name,
            roles=first_permission.roles,
        )
    )


async def test_auth_service_login(db_session, auth_fixtures, user_service, auth_service):
    with pytest.raises(LoginUserNotFoundException):
        await auth_service.login(LoginRequest(email="admin2@mail.com", password="password"))

    with pytest.raises(LoginWrongPasswordException):
        await auth_service.login(LoginRequest(email="admin@mail.com", password="password2"))

    login_user = await auth_service.login(LoginRequest(email="admin@mail.com", password="password"))

    assert login_user.email == "admin@mail.com"


async def test_auth_service_register(db_session, auth_fixtures, user_service, auth_service):
    with pytest.raises(RegisterUserAlreadyExistsException):
        await auth_service.register(RegisterRequest(email="admin@mail.com", password="password"))

    with pytest.raises(RegisterUserPasswordToShortException):
        await auth_service.register(RegisterRequest(email="admin2@mail.com", password="abc"))

    await auth_service.register(RegisterRequest(email="rysev-a@yandex.ru", password="password"))
    user = await user_service.get_one(UserModel.email == "rysev-a@yandex.ru")
    assert validate_activate_code(auth_service.auth_code.code, str(user.id))

    # teardown
    await user_service.delete_where(UserModel.email == "rysev-a@yandex.ru", auto_commit=True)


async def test_auth_service_activate(db_session, auth_fixtures, user_service, auth_service):
    await auth_service.register(RegisterRequest(email="rysev-a@yandex.ru", password="password"))
    activated_user = await auth_service.activate(auth_service.auth_code.code)
    assert activated_user.is_active

    # teardown
    await user_service.delete_where(UserModel.email == "rysev-a@yandex.ru", auto_commit=True)


async def test_auth_service_reset_password_not_found_code(
    db_session, auth_fixtures, user_service, auth_service, auth_code_service
):
    new_password = "new_password"
    with time_machine.travel("2020-01-01 09:00:00"):
        await auth_service.start_reset_password("admin@mail.com")

    with time_machine.travel("2020-01-01 10:00:00"):
        with pytest.raises(ResetPasswordWrongCodeException):
            await auth_service.reset_password(
                ResetPasswordRequest(code=auth_service.auth_code.code, password=new_password)
            )

    with pytest.raises(ResetPasswordNotFoundException):
        await auth_service.reset_password(ResetPasswordRequest(code="00000000", password="newpassword"))

    # teardown
    with time_machine.travel("2020-01-01 09:00:00"):
        await auth_code_service.repository.delete_where(
            AuthCodeModel.code == auth_service.auth_code.code, auto_commit=True
        )


async def test_auth_service_reset_password(db_session, auth_fixtures, user_service, auth_service):
    new_password = "newpassword"

    await auth_service.start_reset_password("admin@mail.com")
    user = await auth_service.reset_password(
        ResetPasswordRequest(code=auth_service.auth_code.code, password=new_password)
    )

    login_user = await auth_service.login(
        LoginRequest(
            email=user.email,
            password=new_password,
        )
    )

    assert login_user.email == "admin@mail.com"

    # teardown
    await user_service.repository.reset_password(user.id, "password")


async def test_set_not_exist_user_password(auth_fixtures, auth_service: AuthService):
    with pytest.raises(SetUserPasswordNotFoundException):
        await auth_service.set_user_password("manager2@mail.com", "newpassword")


async def test_set_user_password(auth_fixtures, auth_service: AuthService):
    await auth_service.set_user_password("manager@mail.com", "newpassword")
    login_user = await auth_service.login(LoginRequest(email="manager@mail.com", password="newpassword"))

    assert login_user.email == "manager@mail.com"

    # teardown
    await auth_service.set_user_password("manager@mail.com", "password")


async def test_update_role_permissions(
    auth_fixtures, auth_service: AuthService, role_service: RoleService, permission_service: PermissionService
):
    role = await role_service.get_one(RoleModel.name == "admin")
    permissions = await permission_service.list(PermissionModel.name == "get")
    await auth_service.update_role_permissions(role.id, {str(permission.id) for permission in permissions})
