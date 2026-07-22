import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings
from app.core.exceptions import EmailError

logger = logging.getLogger("app.email")


class EmailService:
    def __init__(self) -> None:
        templates_dir = Path(__file__).resolve().parent.parent / "templates"
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_owner_notification(self, contact_data: dict, ai_analysis: dict) -> None:
        if settings.smtp_host:
            await self._send_via_smtp(
                to=settings.app_owner_email,
                subject=f"New contact from {contact_data['name']}",
                template="owner_email.html",
                context={"contact": contact_data, "ai": ai_analysis},
            )
        else:
            self._log_email(
                to=settings.app_owner_email,
                subject=f"New contact from {contact_data['name']}",
            )

    async def send_user_copy(self, contact_data: dict) -> None:
        if settings.smtp_host:
            await self._send_via_smtp(
                to=contact_data["email"],
                subject="Copy of your message",
                template="user_email.html",
                context={"contact": contact_data},
            )
        else:
            self._log_email(
                to=contact_data["email"],
                subject="Copy of your message",
            )

    async def _send_via_smtp(self, to: str, subject: str, template: str, context: dict) -> None:
        import aiosmtplib
        from email.message import EmailMessage

        body = self._env.get_template(template).render(**context)

        msg = EmailMessage()
        msg["From"] = settings.smtp_from or settings.app_owner_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body, subtype="html")

        try:
            await aiosmtplib.send(
                msg,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_pass,
                start_tls=True,
            )
        except Exception as e:
            logger.exception("SMTP send failed: to=%s subject=%s", to, subject)
            raise EmailError("Email service unavailable") from e

    def _log_email(self, to: str, subject: str) -> None:
        logger.info("Email logged (SMTP not configured): to=%s subject=%s", to, subject)
