from typing import Annotated, Optional
from uuid import UUID

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from advanced_alchemy.extensions.litestar.providers import create_service_dependencies, FilterConfig
from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.service import OffsetPagination
from litestar import delete, get, patch, post
from litestar.controller import Controller
from litestar.dto import DTOConfig
from litestar.exceptions import HTTPException
from litestar.params import Dependency
from litestar.status_codes import HTTP_409_CONFLICT
import msgspec

from ..models import PermissionModel
from ..permissions import is_admin_guard
from ..services import PermissionService


class PatchPermissionRequest(msgspec.Struct, omit_defaults=True):
    name: Optional[str] = None
    app: Optional[str] = None
    label: Optional[str] = None
    action: Optional[str] = None


class CreatePermissionRequest(msgspec.Struct):
    app: str
    name: str
    label: str
    action: str


class PermissionDTO(SQLAlchemyDTO[PermissionModel]):
    config = DTOConfig(
        exclude={
            "roles",
            "created_at",
            "updated_at",
            "roles.0.created_at",
            "roles.0.updated_at",
        },
        max_nested_depth=1,
    )


class PermissionController(Controller):
    guards = [is_admin_guard]

    dependencies = create_service_dependencies(
        PermissionService,
        key="permissions_service",
        filters=FilterConfig(
            id_filter=UUID,
            created_at=True,
            updated_at=True,
            pagination_type="limit_offset",
        ),
    )

    return_dto = PermissionDTO

    @get(operation_id="ListPermissions", path="/permissions")
    async def list_permissions(
        self,
        permissions_service: PermissionService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[PermissionModel]:
        results, total = await permissions_service.list_and_count(
            *filters, order_by=[PermissionModel.app.asc(), PermissionModel.name.asc()]
        )
        return permissions_service.to_schema(data=results, total=total, filters=filters)

    @get(operation_id="GetPermission", path="/permissions/{permission_id:uuid}")
    async def get_permission(
        self,
        permission_id: UUID,
        permissions_service: PermissionService,
    ) -> PermissionModel:
        return await permissions_service.get(permission_id)

    @delete(operation_id="DeletePermission", path="/permissions/{permission_id:uuid}")
    async def delete_permission(self, permission_id: UUID, permissions_service: PermissionService) -> None:
        await permissions_service.delete(permission_id)

    @patch(operation_id="PatchPermission", path="/permissions/{permission_id:uuid}")
    async def patch_permission(
        self, permission_id: UUID, data: PatchPermissionRequest, permissions_service: PermissionService
    ) -> PermissionModel:
        return await permissions_service.update(PermissionModel(id=permission_id, **msgspec.to_builtins(data)))

    @post(operation_id="CreatePermission", path="/permissions")
    async def create_permission(
        self, data: CreatePermissionRequest, permissions_service: PermissionService
    ) -> PermissionModel:
        if await permissions_service.get_one_or_none(
            PermissionModel.name == data.name, PermissionModel.app == data.app
        ):
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=f"Permission {data.name} already exists")

        return await permissions_service.create(PermissionModel(**msgspec.to_builtins(data)))
