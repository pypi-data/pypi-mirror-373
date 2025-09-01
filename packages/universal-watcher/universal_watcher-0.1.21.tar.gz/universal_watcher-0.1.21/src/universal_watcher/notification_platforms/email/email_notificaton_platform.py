from universal_watcher.core.decorators.injector import (
    DependencyInjector as Injector,
)
from universal_watcher.core.classes.notification_platform.notification_platform import (
    NotificationPlatform,
)
from universal_watcher.notification_platforms.email.models.email_input import (
    EmailInput,
)
from universal_watcher.notification_platforms.email.models.email_parameters import (
    EmailParameters,
)
from universal_watcher.notification_platforms.email.services.email_service import (
    EmailService,
)


@Injector.inject_as_singleton
@Injector.inject_dependencies
class EmailNotificationPlatform(NotificationPlatform):
    NAME = "email"

    def __init__(self, *, email_service: EmailService):
        self._email_service = email_service
        self._params: EmailParameters

    def params(self) -> EmailParameters:
        return self._params

    def set_params(self, params: dict):
        """Setup the data source parameters"""
        self._params = EmailParameters(**params)

    def notify(self, email_data: EmailInput) -> None:
        if not self.params():
            raise ValueError("Parameters not initialized.")

        if not email_data:
            raise ValueError("Email data must be provided.")

        self._email_service.send_email(
            self.params().to,
            email_data.subject,
            email_data.body,
            email_data.content_type,
        )
