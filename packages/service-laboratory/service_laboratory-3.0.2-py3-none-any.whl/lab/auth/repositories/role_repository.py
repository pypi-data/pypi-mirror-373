from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RoleModel


class RoleRepository(SQLAlchemyAsyncRepository):
    model_type = RoleModel


async def provide_role_repository(db_session: AsyncSession) -> RoleRepository:
    return RoleRepository(session=db_session)
