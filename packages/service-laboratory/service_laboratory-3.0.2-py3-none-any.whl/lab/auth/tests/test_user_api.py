from litestar import Litestar
from litestar.testing import AsyncTestClient

from ..models import UserModel
from ..services import UserService


async def test_get_users(
    test_client: AsyncTestClient[Litestar], user_service: UserService, auth_fixtures, admin_headers
) -> None:
    response = await test_client.get("/api/auth/users", headers=admin_headers)
    response_data = response.json()
    assert len(response_data["items"]) == 7
    assert response_data["total"] == 7


async def test_activate_user(
    test_client: AsyncTestClient[Litestar],
    user_service: UserService,
    auth_fixtures,
    admin_headers,
):
    customer = await user_service.repository.get_one(UserModel.email == "customer@mail.com")
    response = await test_client.patch(
        f"/api/auth/users/{customer.id}",
        headers=admin_headers,
        json={"is_active": True},
    )

    await user_service.repository.session.refresh(customer)
    assert customer.is_active == True
