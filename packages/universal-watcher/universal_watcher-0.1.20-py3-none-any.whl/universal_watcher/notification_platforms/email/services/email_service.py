import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from universal_watcher.core.decorators.injector import (
    DependencyInjector as Injector,
)
from universal_watcher.notification_platforms.email.services.email_env_service import (
    EmailEnvService,
)
from universal_watcher.notification_platforms.email.models.email_smtp_config import (
    EmailSmtpConfig,
)


@Injector.inject_as_singleton
@Injector.inject_dependencies
class EmailService:
    def __init__(
        self,
        *,
        dotenv_service: EmailEnvService,
        config: Optional[EmailSmtpConfig] = None,
    ):
        self._smtp_config = config or dotenv_service.get_smtp_config()
        self._smtp = None

    def _open_smtp(self) -> smtplib.SMTP:
        if self._smtp:
            return self._smtp

        encryption = self._smtp_config.encryption
        host = self._smtp_config.host
        port = self._smtp_config.port

        if encryption in ["SSL", "TLS"]:
            smtp = smtplib.SMTP_SSL(host=host, port=port)
        else:
            smtp = smtplib.SMTP(host=host, port=port)
            smtp.starttls()

        smtp.login(
            self._smtp_config.username,
            self._smtp_config.password.get_secret_value(),
        )

        self._smtp = smtp
        return smtp

    def send_email(self, recipient, subject, message, content_type) -> None:
        msg = MIMEMultipart()
        msg["From"] = self._smtp_config.sender_email
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(message, content_type))

        try:
            smtp = self._open_smtp()
            errors = smtp.send_message(msg)
        except Exception as e:
            self._smtp = None
            smtp = self._open_smtp()
            errors = smtp.send_message(msg)
        
        if errors:
            raise ValueError(f"Failed to send email: {errors}")
        
        smtp.quit()
