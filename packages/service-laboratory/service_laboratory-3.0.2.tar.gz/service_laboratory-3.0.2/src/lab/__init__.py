"""
Configure litestar app with lab module:

from litestar import Litestar

from lab.auth.api import auth_router
from lab.auth.auth_cli import CLIPlugin
from lab.core.database import alchemy
from lab.core.openapi import configure_open_api_config


app = Litestar(
    route_handlers=[index, auth_router],
    plugins=[alchemy, CLIPlugin()],
    openapi_config=configure_open_api_config("service template", "2.0.0"),
    debug=True
)
"""
