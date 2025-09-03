from litestar import Litestar
from litestar.testing import AsyncTestClient

from ..models import PermissionModel, RoleModel
from ..services import PermissionService, RoleService, UserService


async def test_get_roles(
    test_client: AsyncTestClient[Litestar],
    user_service: UserService,
    auth_fixtures,
    admin_headers,
) -> None:
    response = await test_client.get("/api/auth/roles", headers=admin_headers)
    response_data = response.json()
    assert len(response_data["items"]) == 4
    assert response_data["total"] == 4


async def test_remove_role(
    test_client: AsyncTestClient[Litestar],
    role_service: RoleService,
    admin_headers,
) -> None:
    role = await role_service.create(RoleModel(name="role_to_remove"), auto_commit=True)
    assert await role_service.count() == 5

    await test_client.delete(f"/api/auth/roles/{role.id}", headers=admin_headers)
    assert await role_service.count() == 4


async def test_create_role(test_client: AsyncTestClient[Litestar], role_service: RoleService, admin_headers):
    power_user_role = await test_client.post("/api/auth/roles", headers=admin_headers, json={"name": "power_user"})
    assert await role_service.count() == 5

    # teardown
    await role_service.delete(power_user_role.json().get("id"), auto_commit=True)


async def test_update_role(
    test_client: AsyncTestClient[Litestar],
    role_service: RoleService,
    permission_service: PermissionService,
    admin_headers,
):
    edit_permission_role = await role_service.create(RoleModel(name="edit_permission_role"), auto_commit=True)
    permissions = await permission_service.list(PermissionModel.name == "get")

    await test_client.patch(
        f"/api/auth/roles/{edit_permission_role.id}",
        json={
            "name": "edit_permission_role updated",
            "permissions": [
                {"id": str(permission.id), "name": permission.name, "app": permission.app} for permission in permissions
            ],
        },
        headers=admin_headers,
    )

    await role_service.repository.session.refresh(edit_permission_role)
    assert edit_permission_role.name == "edit_permission_role updated"

    assert {f"{permission.name} {permission.app}" for permission in edit_permission_role.permissions} == {
        "get users",
        "get roles",
        "get permissions",
    }

    await role_service.delete(edit_permission_role.id, auto_commit=True)
