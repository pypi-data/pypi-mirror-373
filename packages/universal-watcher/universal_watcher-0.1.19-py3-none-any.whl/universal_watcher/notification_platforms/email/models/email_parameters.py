from pydantic import BaseModel, Field, field_validator
import re

from universal_watcher.core.classes.notification_platform.notification_platform_parameters import (
    NotificationPlatformParameters,
)


class EmailParameters(BaseModel, NotificationPlatformParameters):
    to: str = Field(..., description="Recipient email address.")

    @field_validator("to")
    def validate_email(cls, value):
        if not value:
            raise ValueError("Recipient email address must be provided.")

        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email address format.")
        return value
