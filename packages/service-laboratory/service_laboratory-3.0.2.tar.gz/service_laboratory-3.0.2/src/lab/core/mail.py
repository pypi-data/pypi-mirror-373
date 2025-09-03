from email.message import EmailMessage
import smtplib
from typing import List

from ..settings import settings


def send_email(recipients: List[str], subject: str, body: str):
    if settings.is_debug:
        return

    msg = EmailMessage()
    msg.set_content(body)
    server = smtplib.SMTP("smtp.yandex.com", 587)
    server.starttls()
    server.login(settings.email_server_login, "z143abmRQp23")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg.set_content(body)
    msg["From"] = settings.email_server_login

    for recipient in recipients:
        msg["To"] = recipient
        server.send_message(msg)

    server.quit()
