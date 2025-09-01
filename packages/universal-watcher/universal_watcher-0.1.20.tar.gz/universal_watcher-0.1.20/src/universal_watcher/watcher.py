from universal_watcher.core.decorators.injector import (
    DependencyInjector as Injector,
)
from universal_watcher.core.services.db_service import CoreDbService
from universal_watcher.core.services.data_source_registry_service import (
    DataSourcesRegistryService,
)
from universal_watcher.core.services.notification_registry_service import (
    NotificationRegistryService,
)
from universal_watcher.core.classes.data_source.data_source_item import (
    DataSourceItem,
)
from universal_watcher.core.classes.notification_platform.notification_platform_input import (
    NotificationPlatformInput,
)
from universal_watcher.core.models.watcher_model import (
    WatcherModel,
    WatcherDataSourceModel,
    WatcherNotificationPlatformModel,
)


# TODO: Maybe convert this class to a module?
@Injector.inject_dependencies
class Watcher:
    def __init__(
        self,
        *,
        db_service: CoreDbService,
        data_sources_registry_service: DataSourcesRegistryService,
        notification_registry_service: NotificationRegistryService,
    ):
        self._db_service = db_service
        self._data_sources_service = data_sources_registry_service
        self._notifications_service = notification_registry_service

    def create(
        self,
        watcher_name: str,
        data_source_data: dict,
        notification_platform_data: dict,
    ) -> None:
        """
        Create a new watcher with the specified data source and notification platform.

        Args:
            watcher_name (str): The unique name of the watcher.
            data_source_data (dict): Configuration data for the data source.
            notification_platform_data (dict): Configuration data for the notification platform.

        Raises:
            ValueError: If the watcher already exists.
        """
        # Validate the data source parameters
        data_source_name = data_source_data["name"]
        data_source_class = (
            self._data_sources_service.get_data_source_parameters_class(
                data_source_name
            )
        )
        data_source_parameters = data_source_class(
            **data_source_data["parameters"]
        )
        data_source_data["parameters"] = data_source_parameters.model_dump()

        # Validate the notification platform parameters
        notification_platform_name = notification_platform_data["name"]
        notification_platform_class = self._notifications_service.get_notification_platform_parameters_class(
            notification_platform_name
        )
        notification_platform_parameters = notification_platform_class(
            **notification_platform_data["parameters"]
        )
        notification_platform_data["parameters"] = (
            notification_platform_parameters.model_dump()
        )

        self._db_service.create_watcher(
            WatcherModel(
                name=watcher_name,
                data_source=WatcherDataSourceModel(**data_source_data),
                notification_platform=WatcherNotificationPlatformModel(
                    **notification_platform_data
                ),
            )
        )

    def update(
        self,
        current_watcher_name: str,
        new_watcher_name: str,
        data_source_data: dict,
        notification_platform_data: dict,
    ) -> None:
        """
        Update the name od the watcher, data source and notification platform
        for the specified watcher.

        Args:
            current_watcher_name (str): The name of the watcher to update.
            new_watcher_name (str): The new name for the watcher.
            data_source_data (dict): Configuration data for the data source.
            notification_platform_data (dict): Configuration data for the notification platform.

        Raises:
            ValueError: If the watcher does not exist.
        """
        # Validate the data source parameters
        data_source_name = data_source_data["name"]
        data_source_class = (
            self._data_sources_service.get_data_source_parameters_class(
                data_source_name
            )
        )
        data_source_parameters = data_source_class(
            **data_source_data["parameters"]
        )
        data_source_data["parameters"] = data_source_parameters.model_dump()

        # Validate the notification platform parameters
        notification_platform_name = notification_platform_data["name"]
        notification_platform_class = self._notifications_service.get_notification_platform_parameters_class(
            notification_platform_name
        )
        notification_platform_parameters = notification_platform_class(
            **notification_platform_data["parameters"]
        )
        notification_platform_data["parameters"] = (
            notification_platform_parameters.model_dump()
        )

        self._db_service.set_watcher_data(
            current_watcher_name,
            new_watcher_name,
            data_source=WatcherDataSourceModel(**data_source_data),
            notification_platform=WatcherNotificationPlatformModel(
                **notification_platform_data
            ),
        )

    def get_new_data(
        self, watcher_name: str, update_current: bool = False
    ) -> list[DataSourceItem]:
        """
        Retrieve new data items for the specified watcher.

        Args:
            watcher_name (str): The name of the watcher.
            update_current (bool, optional): Whether to update the stored items with fetched data. Defaults to False.

        Raises:
            ValueError: If parameters are not initialized.

        Returns:
            list[DataSourceItem]: List of new data items.
        """
        watcher_data = self._db_service.get_watcher_data(watcher_name)
        data_source = self._data_sources_service.get_data_source(
            watcher_data["data_source"]["name"]
        )
        data_source.set_params(watcher_data["data_source"]["parameters"])

        current_items = data_source.get_stored_items(watcher_name)
        items = data_source.fetch_items()

        if update_current:
            self._db_service.set_watcher_items(watcher_name, items)

        return [item for item in items if item not in current_items]

    def format_items(
        self,
        data_source_name: str,
        formatter_name: str,
        items: list[DataSourceItem],
    ) -> NotificationPlatformInput:
        """
        Format the given items using the specified formatter.

        Args:
            data_source_name (str): Name of the data source.
            formatter_name (str): Name of the formatter to use.
            items (list[DataSourceItem]): Items to format.

        Raises:
            ValueError: If the formatter is not found.

        Returns:
            NotificationPlatformInput: Formatted data ready for notification.
        """
        data_source = self._data_sources_service.get_data_source(
            data_source_name
        )
        return data_source.format_items(formatter_name, items)

    def send_notification(
        self,
        watcher_name: str,
        notification_platform_input: NotificationPlatformInput,
    ) -> None:
        """
        Send a notification using the specified watcher's notification platform.

        Args:
            watcher_name (str): The name of the watcher.
            notification_platform_input (NotificationPlatformInput): The formatted notification data.

        Raises:
            ValueError: If parameters are not initialized or notification data is invalid.
        """
        watcher_data = self._db_service.get_watcher_data(watcher_name)
        notif_platform = self._notifications_service.get_notification_platform(
            watcher_data["notification_platform"]["name"]
        )
        notif_platform.set_params(
            watcher_data["notification_platform"]["parameters"]
        )
        notif_platform.notify(notification_platform_input)

    def check(self, watcher_name: str) -> None:
        """
        Check for new data items for the specified watcher and send notifications if new items are found.

        Args:
            watcher_name (str): The name of the watcher.

        Raises:
            ValueError: If parameters are not initialized or notification data is invalid.
        """
        watcher_data = self._db_service.get_watcher_data(watcher_name)
        new_items = self.get_new_data(watcher_name, update_current=True)

        # Initial population, or no new items - do not notify
        if not new_items:
            return

        notification_platform_input = self.format_items(
            watcher_data["data_source"]["name"],
            watcher_data["data_source"]["formatter"],
            new_items,
        )

        self.send_notification(watcher_name, notification_platform_input)

    def check_all(self) -> None:
        """
        Check all watchers for new data items and send notifications accordingly.
        """
        watchers_names = self._db_service.get_all_watchers()
        for watcher_name in watchers_names:
            self.check(watcher_name)

    def delete(self, watcher_name: str) -> None:
        """
        Delete the specified watcher.

        Args:
            watcher_name (str): The name of the watcher.

        Raises:
            ValueError: If the watcher does not exist.
        """
        self._db_service.delete_watcher(watcher_name)