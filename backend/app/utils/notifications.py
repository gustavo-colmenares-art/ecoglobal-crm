import logging

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.config import settings

logger = logging.getLogger("ecoglobal.notifications")

_conf = ConnectionConfig(
    MAIL_USERNAME=settings.smtp_user,
    MAIL_PASSWORD=settings.smtp_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.smtp_port,
    MAIL_SERVER=settings.smtp_host,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=bool(settings.smtp_user),
    VALIDATE_CERTS=False,
    SUPPRESS_SEND=0 if settings.smtp_host else 1,
)


async def enviar_email(destinatarios: list[str], asunto: str, cuerpo_html: str) -> None:
    if not destinatarios:
        return
    try:
        message = MessageSchema(
            subject=asunto,
            recipients=destinatarios,
            body=cuerpo_html,
            subtype=MessageType.html,
        )
        await FastMail(_conf).send_message(message)
    except Exception:
        logger.exception("No se pudo enviar el correo de alerta: %s", asunto)
