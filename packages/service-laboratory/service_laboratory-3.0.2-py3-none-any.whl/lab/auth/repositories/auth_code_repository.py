from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AuthCodeModel


class AuthCodeRepository(SQLAlchemyAsyncRepository):
    model_type = AuthCodeModel

async def provide_auth_code_repository(db_session: AsyncSession) -> AuthCodeRepository:
    return AuthCodeRepository(session=db_session)
