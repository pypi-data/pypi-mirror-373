from litestar import Request
from litestar.events import listener

from ..core.mail import send_email


@listener("send_auth_code")
async def send_auth_code_handler(email: str, code: str) -> None:
    send_email([email], "Account auth code", f"Auth code: {code}")


async def provide_emit_event(request: Request):
    def emit_event(*args, **kwargs):
        return request.app.emit(*args, **kwargs)

    return emit_event
