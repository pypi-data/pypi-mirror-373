from litestar import Router

from .account_controller import AccountController
from .permission_controller import PermissionController
from .role_controller import RoleController
from .user_controller import UserController

auth_router = Router(
    path="/api/auth",
    route_handlers=[
        RoleController,
        UserController,
        AccountController,
        PermissionController,
    ],
)
