from litestar import Litestar
from litestar.testing import AsyncTestClient

from ..models import PermissionModel
from ..services import PermissionService


async def test_get_permissions(
    test_client: AsyncTestClient[Litestar],
    auth_fixtures,
    admin_headers,
) -> None:
    response = await test_client.get("/api/auth/permissions", headers=admin_headers)
    response_data = response.json()
    assert len(response_data["items"]) == 12
    assert response_data["total"] == 12


async def test_remove_permission(
    test_client: AsyncTestClient[Litestar],
    permission_service: PermissionService,
    admin_headers,
) -> None:
    permission = await permission_service.create(
        PermissionModel(name="permission_to_remove", app="users"), auto_commit=True
    )
    assert await permission_service.count() == 13

    await test_client.delete(f"/api/auth/permissions/{permission.id}", headers=admin_headers)
    assert await permission_service.count() == 12


async def test_create_permission(
    test_client: AsyncTestClient[Litestar], permission_service: PermissionService, admin_headers
):
    remove_user_permission = await test_client.post(
        "/api/auth/permissions", headers=admin_headers, json={"name": "remove-user", "app": "auth"}
    )
    assert await permission_service.count() == 13

    # teardown
    await permission_service.delete(remove_user_permission.json().get("id"), auto_commit=True)


async def test_create_permission_with_exist_name_and_app(
    test_client: AsyncTestClient[Litestar], permission_service: PermissionService, admin_headers
):
    await test_client.post(
        "/api/auth/permissions",
        headers=admin_headers,
        json={"name": "get", "app": "users"},
    )
    assert await permission_service.count() == 12


async def test_update_permission(
    test_client: AsyncTestClient[Litestar],
    permission_service: PermissionService,
    admin_headers,
):
    updated_permission = await permission_service.create(
        PermissionModel(name="set-user-password", app="auth"), auto_commit=True
    )

    await test_client.patch(
        f"/api/auth/permissions/{updated_permission.id}",
        headers=admin_headers,
        json={"name": "remove-user-password", "app": "auth"},
    )

    await permission_service.repository.session.refresh(updated_permission)
    assert updated_permission.name == "remove-user-password"

    # teardown
    await permission_service.delete(updated_permission.id, auto_commit=True)
