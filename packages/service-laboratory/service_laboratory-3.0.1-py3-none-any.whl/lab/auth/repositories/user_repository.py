import uuid

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import RoleModel, UserModel, UserRoleAssociation


class UserRepository(SQLAlchemyAsyncRepository):
    model_type = UserModel

    async def create_admin(
        self,
        user: UserModel,
    ) -> UserModel:
        user = await self.add(user, auto_commit=True)
        return await self.add_user_role(
            user,
            "admin",
        )

    async def add_user_role(
        self,
        user: UserModel,
        role_name: str,
    ) -> UserModel:
        role = await self.session.scalar(select(RoleModel).where(RoleModel.name == role_name))
        await self.session.execute(insert(UserRoleAssociation).values(user_id=user.id, role_id=role.id))
        await self.session.commit()
        return user

    async def activate(self, user_id: uuid.UUID):
        return await self.update(
            UserModel(
                id=user_id,
                is_active=True,
            ),
            auto_commit=True,
        )

    async def reset_password(self, user_id: uuid.UUID, password: str):
        return await self.update(
            UserModel(
                id=user_id,
                password=password,
            ),
            auto_commit=True,
        )


async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(session=db_session)
