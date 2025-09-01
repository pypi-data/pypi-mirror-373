from __future__ import annotations

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from ..models import PermissionModel
from ..repositories import PermissionRepository

__all__ = ("PermissionService",)


class PermissionService(SQLAlchemyAsyncRepositoryService[PermissionModel, PermissionRepository]):
    repository_type = PermissionRepository
