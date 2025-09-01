from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class UserRoleAssociation(UUIDAuditBase):
    __tablename__ = "users_roles"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class RolePermissionAssociation(UUIDAuditBase):
    __tablename__ = "roles_permissions"

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id"), primary_key=True)
