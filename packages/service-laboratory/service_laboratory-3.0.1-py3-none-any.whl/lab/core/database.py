from litestar.plugins.sqlalchemy import AsyncSessionConfig, SQLAlchemyAsyncConfig
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..settings import settings

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.database_uri,
    before_send_handler="autocommit",
    session_config=session_config,
)


engine = create_async_engine(settings.database_uri, echo=False)
session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
