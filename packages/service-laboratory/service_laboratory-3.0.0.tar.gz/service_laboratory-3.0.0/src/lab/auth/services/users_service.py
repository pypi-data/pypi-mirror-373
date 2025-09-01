from __future__ import annotations

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from ..models import UserModel
from ..repositories import UserRepository

__all__ = ("UserService",)


class UserService(SQLAlchemyAsyncRepositoryService[UserModel, UserRepository]):
    match_fields = ["email"]
    repository_type = UserRepository



