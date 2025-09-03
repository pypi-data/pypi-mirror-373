from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column, relationship


class UserModel(UUIDAuditBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column()
    is_enabled: Mapped[bool] = mapped_column(default=True)
    is_active: Mapped[bool] = mapped_column(default=False)

    roles = relationship(
        "RoleModel",
        secondary="users_roles",
        back_populates="users",
        lazy="selectin",
    )

    def __str__(self):
        return self.email
