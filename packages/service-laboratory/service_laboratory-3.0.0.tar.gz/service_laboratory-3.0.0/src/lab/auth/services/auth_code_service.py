from __future__ import annotations

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService

from ..models import AuthCodeModel
from ..repositories import AuthCodeRepository

__all__ = ("AuthCodeService",)


class AuthCodeService(SQLAlchemyAsyncRepositoryService[AuthCodeModel, AuthCodeRepository]):
    repository_type = AuthCodeRepository
