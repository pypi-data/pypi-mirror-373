from abc import ABC, abstractmethod

from ..notification_platform.notification_platform_input import (
    NotificationPlatformInput,
)
from ..data_source.data_source_item import DataSourceItem


class Formatter(ABC):
    @abstractmethod
    def format_items(
        self, items: list[DataSourceItem]
    ) -> NotificationPlatformInput:
        """Format the items"""
        pass
