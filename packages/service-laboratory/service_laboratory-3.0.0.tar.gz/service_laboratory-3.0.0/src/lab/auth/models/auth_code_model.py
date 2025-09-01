from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class AuthCodeModel(UUIDAuditBase):
    __tablename__ = "auth_codes"

    code: Mapped[str] = mapped_column()
    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
