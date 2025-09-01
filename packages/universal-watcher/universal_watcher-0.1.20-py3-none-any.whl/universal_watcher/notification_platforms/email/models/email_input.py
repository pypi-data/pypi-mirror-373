from pydantic import BaseModel

from universal_watcher.core.classes.notification_platform.notification_platform_input import (
    NotificationPlatformInput,
)


class EmailInput(BaseModel, NotificationPlatformInput):
    subject: str
    body: str
    content_type: str
