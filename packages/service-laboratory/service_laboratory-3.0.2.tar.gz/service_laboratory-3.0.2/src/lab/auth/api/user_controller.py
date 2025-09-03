from dataclasses import dataclass
from typing import Annotated, List, Optional
from uuid import UUID

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from advanced_alchemy.extensions.litestar.providers import create_service_dependencies, FilterConfig
from advanced_alchemy.filters import FilterTypes
from advanced_alchemy.service import OffsetPagination
from litestar import delete, get, patch
from litestar.controller import Controller
from litestar.di import Provide
from litestar.dto import DataclassDTO, DTOConfig
from litestar.params import Dependency

from ..auth_events import provide_emit_event
from ..models import UserModel
from ..permissions import is_admin_guard
from ..services import AuthService, UserService, provide_auth_service


@dataclass
class UserData:
    id: UUID
    email: str
    is_enabled: bool
    is_active: bool
    password: str


@dataclass
class UserRolePatchData:
    id: str
    name: str


import msgspec


class UserPatchData(msgspec.Struct, omit_defaults=True):
    email: Optional[str] = None
    password: Optional[str] = None
    is_enabled: Optional[bool] = None
    is_active: Optional[bool] = None
    roles: Optional[List[UserRolePatchData]] = None


class PatchUserDTO(DataclassDTO[UserPatchData]):
    config = DTOConfig(exclude={"id"}, partial=True)


class UserDTO(SQLAlchemyDTO[UserModel]):
    config = DTOConfig(
        exclude={
            "password",
            "created_at",
            "updated_at",
            "roles.0.created_at",
            "roles.0.updated_at",
        },
        max_nested_depth=1,
    )


class UserController(Controller):
    guards = [is_admin_guard]

    dependencies = {
        "emit_event": Provide(provide_emit_event),
        "auth_service": Provide(provide_auth_service),
        **create_service_dependencies(
            UserService,
            key="users_service",
            load=[UserModel.roles],
            filters=FilterConfig(
                id_filter=UUID,
                created_at=True,
                updated_at=True,
                pagination_type="limit_offset",
                search="email",
            ),
        ),
    }

    return_dto = UserDTO

    @get(operation_id="ListUsers", path="/users")
    async def list_users(
        self,
        users_service: UserService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[UserModel]:
        results, total = await users_service.list_and_count(*filters)
        return users_service.to_schema(data=results, total=total, filters=filters)

    @delete(operation_id="RemoveUser", path="/users/{user_id:str}")
    async def remove_user(self, users_service: UserService, user_id: UUID) -> None:
        await users_service.delete(user_id, auto_commit=True)
        return None

    @get(operation_id="GetUser", path="/users/{user_id:str}")
    async def get_user(self, user_id: UUID, users_service: UserService) -> UserModel:
        return await users_service.get(user_id)

    @patch(operation_id="UpdateUser", path="/users/{user_id:str}")
    async def update_user(
        self, user_id: UUID, users_service: UserService, auth_service: AuthService, data: UserPatchData
    ) -> UserModel:
        user = await users_service.get(user_id)
        data = msgspec.to_builtins(data)

        if data.get("roles") is not None:
            roles = data.pop("roles")
            await auth_service.update_user_roles(user_id, roles)

        await users_service.update(UserModel(id=user_id, **data), auto_commit=True)

        return users_service.to_schema(data=user)
