from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from ..models import UserRoleAssociation


class UserRoleAssociationRepository(SQLAlchemyAsyncRepository):
    model_type = UserRoleAssociation
