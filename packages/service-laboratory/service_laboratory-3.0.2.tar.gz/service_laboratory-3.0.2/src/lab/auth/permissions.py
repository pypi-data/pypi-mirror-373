from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler


def is_admin_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    user_roles = [item.get("name") for item in connection.user.get("roles")]
    if "admin" not in user_roles:
        raise NotAuthorizedException("only admins can access this api")
