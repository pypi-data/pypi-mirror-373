from __future__ import annotations

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from ..models import RoleModel
from ..repositories import RoleRepository

__all__ = ("RoleService",)


class RoleService(SQLAlchemyAsyncRepositoryService[RoleModel, RoleRepository]):
    repository_type = RoleRepository
