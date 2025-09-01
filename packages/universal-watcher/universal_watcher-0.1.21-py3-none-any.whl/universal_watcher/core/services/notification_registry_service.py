from typing import Type, Union
from pydantic import BaseModel
import importlib

from ..classes.notification_platform.notification_platform import (
    NotificationPlatform,
)


class NotificationRegistryService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Creates a singleton instance of NotificationRegistryService.

        Initializes the notification_platforms list if the instance does not exist.
        """
        if cls._instance is None:
            cls._instance = super(NotificationRegistryService, cls).__new__(
                cls, *args, **kwargs
            )
            cls._instance._notification_platforms = []
        return cls._instance

    def get_notification_platforms(self) -> list[dict]:
        """
        Retrieves the list of registered notification platforms.

        Returns:
            list: A list of notification platform dictionaries.
        """
        return self._notification_platforms

    def _get_notification_platform_entry(self, name: str) -> Union[dict, None]:
        """
        Retrieves data for a specific notification platform by name.

        Args:
            name (str): The name of the notification platform.

        Returns:
            Union[dict, None]: The notification platform dictionary if found, else None.
        """
        for platform in self.get_notification_platforms():
            if platform["name"] == name:
                return platform
        return None

    def register_notification_platform(
        self, name: str, cls_type: Type[NotificationPlatform]
    ) -> None:
        """
        Registers a new notification platform. Raises an error if a platform with the given name already exists.

        Args:
            name (str): The name of the notification platform.
            cls_type (Type[Notification]): The class type of the notification platform.

        Raises:
            ValueError: If a notification platform with the given name already exists.
        """
        if self._get_notification_platform_entry(name):
            raise ValueError(
                f"A notification platform with the name '{name}' already exists."
            )

        self._notification_platforms.append({"name": name, "class": cls_type})

    def get_notification_platform(self, name: str) -> NotificationPlatform:
        """
        Retrieves a notification platform instance by name.

        Args:
            name (str): The name of the notification platform.

        Returns:
            NotificationPlatform: An instance of the requested Notification platform.

        Raises:
            ValueError: If the notification platform with the given name is not found.
        """
        data = self._get_notification_platform_entry(name)

        if not data:
            raise ValueError(f"Notification platform '{name}' not found.")

        return data["class"]()

    def get_notification_platform_name(
        self, cls_type: Type[NotificationPlatform]
    ) -> str:
        """
        Retrieves the name of a notification platform given its class type.

        Args:
            cls_type (Type[Notification]): The class type of the notification platform.

        Raises:
            ValueError: If no notification platform with the given class type is found.

        Returns:
            str: The name of the notification platform.
        """
        for platform in self.get_notification_platforms():
            if platform["class"] == cls_type:
                return platform["name"]

        raise ValueError(f"Notification platform {cls_type} not found.")

    def get_notification_platform_parameters_class(self, name: str) -> Type[BaseModel]:
        """
        Retrieves the parameters class of a notification platform by name.

        Args:
            name (str): The name of the notification platform.

        Raises:
            ValueError: If the notification platform with the given name is not found.

        Returns:
            Type: The class of the notification platform parameters.
        """
        data = self._get_notification_platform_entry(name)

        if not data:
            raise ValueError(f"Notification platform {name} not found.")

        try:
            module_path = f"universal_watcher.notification_platforms.{name}.models.{name}_parameters"
            module = importlib.import_module(module_path)

            class_name = (
                "".join(word.capitalize() for word in name.split("_"))
                + "Parameters"
            )

            return getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ValueError(f"Invalid notification platform or class name: {e}")