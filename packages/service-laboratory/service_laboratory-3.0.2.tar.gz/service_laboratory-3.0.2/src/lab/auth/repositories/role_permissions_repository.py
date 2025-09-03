from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from ..models import RolePermissionAssociation


class RolePermissionAssociationRepository(SQLAlchemyAsyncRepository):
    model_type = RolePermissionAssociation
