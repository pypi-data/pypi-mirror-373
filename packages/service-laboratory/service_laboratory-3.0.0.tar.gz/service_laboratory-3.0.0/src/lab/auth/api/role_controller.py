from typing import Annotated, List, Optional
import uuid
from uuid import UUID

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from advanced_alchemy.extensions.litestar.providers import create_service_dependencies, FilterConfig
from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.service import OffsetPagination
from litestar import delete, get, patch, post
from litestar.controller import Controller
from litestar.di import Provide
from litestar.dto import DTOConfig
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from litestar.status_codes import HTTP_409_CONFLICT
import msgspec

from ..auth_events import provide_emit_event
from ..models import RoleModel
from ..permissions import is_admin_guard
from ..services import AuthService, RoleService, provide_auth_service


class CreateRoleRequest(msgspec.Struct):
    name: str


class RolePermissionPatchData(msgspec.Struct):
    id: uuid.UUID
    name: str


class PatchRoleRequest(msgspec.Struct, omit_defaults=True):
    name: Optional[str] = None
    permissions: Optional[List[RolePermissionPatchData]] = None


class RoleDTO(SQLAlchemyDTO[RoleModel]):
    config = DTOConfig(
        exclude={
            "users",
            "created_at",
            "updated_at",
            "permissions.0.created_at",
            "permissions.0.updated_at",
        },
        max_nested_depth=1,
    )


class RoleController(Controller):
    guards = [is_admin_guard]
    dependencies = {
        "auth_service": Provide(provide_auth_service),
        "emit_event": Provide(provide_emit_event),
        **create_service_dependencies(
            RoleService,
            key="roles_service",
            load=[RoleModel.permissions],
            filters=FilterConfig(
                id_filter=UUID,
                created_at=True,
                updated_at=True,
                pagination_type="limit_offset",
            ),
        ),
    }

    return_dto = RoleDTO

    @get(operation_id="ListRoles", path="/roles")
    async def list_roles(
        self,
        roles_service: RoleService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[RoleModel]:
        results, total = await roles_service.list_and_count(*filters)
        return roles_service.to_schema(data=results, total=total, filters=filters)

    @get(operation_id="GetRole", path="/roles/{role_id:uuid}")
    async def get_role(
        self,
        role_id: UUID,
        roles_service: RoleService,
    ) -> RoleModel:
        return await roles_service.get(role_id)

    @delete(operation_id="DeleteRole", path="/roles/{role_id:uuid}")
    async def delete_role(self, role_id: UUID, roles_service: RoleService) -> None:
        await roles_service.delete(role_id)

    @patch(operation_id="PatchRole", path="/roles/{role_id:uuid}")
    async def patch_role(
        self,
        role_id: UUID,
        data: PatchRoleRequest,
        roles_service: RoleService,
        auth_service: AuthService,
    ) -> RoleModel:
        data = msgspec.to_builtins(data)
        if data.get("permissions"):
            await auth_service.update_role_permissions(
                role_id, {permission.get("id") for permission in data.pop("permissions")}
            )

        return await roles_service.update(RoleModel(id=role_id, **data), auto_commit=True)

    @post(operation_id="CreateRole", path="/roles")
    async def create_role(self, data: CreateRoleRequest, roles_service: RoleService) -> RoleModel:
        if await roles_service.get_one_or_none(RoleModel.name == data.name):
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=f"Role {data.name} already exists")

        return await roles_service.create(RoleModel(**msgspec.to_builtins(data)))
