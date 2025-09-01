from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import PermissionModel


class PermissionRepository(SQLAlchemyAsyncRepository):
    model_type = PermissionModel


async def provide_permission_repository(db_session: AsyncSession) -> PermissionRepository:
    return PermissionRepository(session=db_session)
