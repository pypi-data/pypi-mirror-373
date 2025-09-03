from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme


def configure_open_api_config(title: str, version: str, path: str = "/api/docs"):
    return OpenAPIConfig(
        components=[
            Components(
                security_schemes={
                    "JWT": SecurityScheme(
                        type="http",
                        scheme="Bearer",
                        name="Authorization",
                        security_scheme_in="cookie",
                        bearer_format="JWT",
                        description="Authorization",
                    )
                }
            )
        ],
        title=title,
        version=version,
        path=path,
        render_plugins=[ScalarRenderPlugin()],
    )
