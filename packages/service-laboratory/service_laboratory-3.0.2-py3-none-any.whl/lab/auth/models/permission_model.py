from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PermissionModel(UUIDAuditBase):
    __tablename__ = "permissions"

    app: Mapped[str] = mapped_column()
    action: Mapped[str] = mapped_column()

    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    label: Mapped[str] = mapped_column(unique=True, nullable=False)

    roles = relationship(
        "RoleModel",
        secondary="roles_permissions",
        back_populates="permissions",
    )

    __table_args__ = (UniqueConstraint("app", "action", name="_permission_info"),)
