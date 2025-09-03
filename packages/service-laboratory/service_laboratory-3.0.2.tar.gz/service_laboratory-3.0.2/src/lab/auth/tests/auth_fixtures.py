from typing import Dict

import pytest

from ..api import AccountController
from ..auth_cli import AuthLoader
from ..middleware import API_KEY_HEADER, TOKEN_PREFIX
from ..models import UserModel
from ..services import AuthCodeService, AuthService, PermissionService, RoleService, UserService


@pytest.fixture(scope="session")
async def auth_fixtures(db_session):
    auth_loader = AuthLoader(db_session)
    await auth_loader.generate_data()
    yield
    await auth_loader.clear_data()


@pytest.fixture(scope="session")
async def user_service(db_session) -> UserService:
    return UserService(db_session)


@pytest.fixture(scope="session")
async def role_service(db_session) -> RoleService:
    return RoleService(db_session)


@pytest.fixture(scope="session")
async def permission_service(db_session) -> PermissionService:
    return PermissionService(db_session)


@pytest.fixture(scope="session")
async def auth_code_service(db_session) -> AuthCodeService:
    return AuthCodeService(db_session)


@pytest.fixture(scope="session")
async def auth_service(db_session) -> AuthService:
    def emit_event(*args, **kwargs): ...

    return AuthService(db_session, emit_event=emit_event)


@pytest.fixture(scope="session")
async def admin_headers(auth_fixtures, user_service: UserService) -> Dict[str, str]:
    admin = await user_service.repository.get_one(UserModel.email == "admin@mail.com")
    access_token = AccountController.generate_token(admin)
    return {"Accept": "application/json", API_KEY_HEADER: f"{TOKEN_PREFIX}{access_token}"}
