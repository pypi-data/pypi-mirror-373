from litestar import Litestar
from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from litestar.testing import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession
import time_machine

from ..api import AccountController
from ..middleware import API_KEY_HEADER, TOKEN_PREFIX
from ..models import UserModel
from ..services import AuthService, RegisterRequest, UserService


async def test_login(test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures) -> None:
    admin = await user_service.repository.get_one(UserModel.email == "admin@mail.com")

    response = await test_client.post(
        "/api/auth/account/login",
        json={
            "email": admin.email,
            "password": "password",
        },
    )

    assert response.status_code == HTTP_201_CREATED


async def test_login_with_invalid_email(
    test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures
) -> None:
    admin = await user_service.repository.get_one(UserModel.email == "admin@mail.com")
    response = await test_client.post(
        "/api/auth/account/login",
        json={
            "email": admin.email + "_invalid_email",
            "password": "password",
        },
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "User with email admin@mail.com_invalid_email not found",
        "status_code": 404,
    }


async def test_login_with_invalid_password(
    test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures
) -> None:
    admin = await user_service.repository.get_one(UserModel.email == "admin@mail.com")
    response = await test_client.post(
        "/api/auth/account/login",
        json={
            "email": admin.email,
            "password": "password" + "_invalid_password",
        },
    )
    assert response.status_code == HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Invalid password",
        "status_code": 404,
    }


async def test_success_register(
    test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures
) -> None:
    register_user_email = "register_user@mail.com"
    response = await test_client.post(
        "/api/auth/account/register",
        json={
            "email": register_user_email,
            "password": "password",
        },
    )

    register_user = await user_service.repository.get_one(UserModel.email == register_user_email)
    assert register_user.is_active == False
    assert response.status_code == HTTP_201_CREATED
    await user_service.repository.delete(register_user.id)


async def test_register_with_exist_email(
    test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures
) -> None:
    register_user_email = "admin@mail.com"
    response = await test_client.post(
        "/api/auth/account/register",
        json={
            "email": register_user_email,
            "password": "password",
        },
    )
    assert response.status_code == HTTP_409_CONFLICT
    assert response.json()["detail"] == "User already exists"


async def test_register_with_too_short_password(
    test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures
) -> None:
    register_user_email = "register_new_user@mail.com"
    response = await test_client.post(
        "/api/auth/account/register",
        json={
            "email": register_user_email,
            "password": "abc",
        },
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Password too short"


async def test_get_account(test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures) -> None:
    admin = await user_service.repository.get_one(UserModel.email == "admin@mail.com")
    access_token = AccountController.generate_token(admin)
    response = await test_client.get(
        "/api/auth/account/me", headers={"Accept": "application/json", API_KEY_HEADER: f"{TOKEN_PREFIX}{access_token}"}
    )
    response_data = response.json()
    assert response_data.get("email") == admin.email


async def test_success_activate_user(
    test_client: AsyncTestClient[Litestar],
    user_service: UserService,
    auth_service: AuthService,
    db_session: AsyncSession,
    auth_fixtures,
) -> None:
    await auth_service.register(RegisterRequest(email="rysev-a@yandex.ru", password="password"))
    user = await user_service.get_one(UserModel.email == "rysev-a@yandex.ru")

    assert user.is_active == False

    await test_client.post(
        "/api/auth/account/activate",
        json={"code": auth_service.auth_code.code},
    )

    await db_session.refresh(user)
    assert user.is_active == True
    await user_service.repository.delete(user.id, auto_commit=True)


async def test_activate_user_wrong_code(
    test_client: AsyncTestClient[Litestar],
    user_service: UserService,
    auth_service: AuthService,
    db_session: AsyncSession,
    auth_fixtures,
):
    await auth_service.register(RegisterRequest(email="rysev-a@yandex.ru", password="password"))
    user = await user_service.get_one(UserModel.email == "rysev-a@yandex.ru")

    assert user.is_active == False

    response = await test_client.post(
        "/api/auth/account/activate",
        json={"code": "00000000"},
    )

    await db_session.refresh(user)
    assert user.is_active == False

    assert response.json() == {"detail": "Auth code not found", "status_code": 404}

    await user_service.repository.delete(user.id, auto_commit=True)


async def test_activate_user_expired_code(
    test_client: AsyncTestClient[Litestar],
    user_service: UserService,
    auth_service: AuthService,
    db_session: AsyncSession,
    auth_fixtures,
):
    with time_machine.travel("2020-01-01 09:00"):
        await auth_service.register(RegisterRequest(email="rysev-a@yandex.ru", password="password"))
        user = await user_service.get_one(UserModel.email == "rysev-a@yandex.ru")

        assert user.is_active == False

    with time_machine.travel("2020-01-01 10:00"):
        response = await test_client.post(
            "/api/auth/account/activate",
            json={"code": auth_service.auth_code.code},
        )

        await db_session.refresh(user)
        assert user.is_active == False
        assert response.json() == {"detail": "Auth code wrong or expired", "status_code": 400}

        await user_service.repository.delete(user.id, auto_commit=True)
