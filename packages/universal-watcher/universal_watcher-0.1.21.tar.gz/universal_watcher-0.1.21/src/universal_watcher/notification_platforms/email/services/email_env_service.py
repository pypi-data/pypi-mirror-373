import os

from universal_watcher.core.decorators.injector import (
    DependencyInjector as Injector,
)
from universal_watcher.notification_platforms.email.models.email_smtp_config import (
    EmailSmtpConfig,
)


@Injector.inject_as_singleton
class EmailEnvService:
    def get_smtp_config(self) -> EmailSmtpConfig:
        return EmailSmtpConfig(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
            encryption=os.getenv("SMTP_ENCRYPTION"),
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
            sender_email=os.getenv("SMTP_SENDER_EMAIL"),
        )
