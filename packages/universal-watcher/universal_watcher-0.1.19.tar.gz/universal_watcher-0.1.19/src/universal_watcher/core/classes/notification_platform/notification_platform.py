from abc import ABC, abstractmethod

from .notification_platform_input import NotificationPlatformInput
from .notification_platform_parameters import NotificationPlatformParameters


class NotificationPlatform(ABC):
    @abstractmethod
    def params(self) -> NotificationPlatformParameters:
        """Parameters for the data source"""
        pass

    @abstractmethod
    def set_params(self, params: dict) -> None:
        """Setup the data source parameters"""
        pass

    @abstractmethod
    def notify(self, input_data: NotificationPlatformInput) -> None:
        """Notify the user about new items"""
        pass
