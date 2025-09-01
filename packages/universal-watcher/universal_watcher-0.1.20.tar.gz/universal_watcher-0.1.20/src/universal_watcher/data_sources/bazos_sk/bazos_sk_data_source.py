from ...core.decorators.injector import DependencyInjector as Injector
from ...core.classes.data_source.data_source import DataSource
from ...core.classes.formatter.formatter import Formatter
from .services.bazos_sk_data_service import (
    BazosSkDataService,
)
from .services.bazos_sk_db_service import BazosSkDbService
from .services.bazos_sk_formatter_service import (
    BazosSkFormatterService,
)
from .models.bazos_sk_parameters import BazosSkParameters
from .models.bazos_sk_item import BazosSkItem
from ...core.classes.notification_platform.notification_platform_input import (
    NotificationPlatformInput,
)


@Injector.inject_as_singleton
@Injector.inject_dependencies
class BazosSkDataSource(DataSource):
    NAME = "bazos_sk"

    def __init__(
        self,
        *,
        data_service: BazosSkDataService,
        db_service: BazosSkDbService,
        formatter_service: BazosSkFormatterService,
    ):
        self._data_service = data_service
        self._db_service = db_service
        self._formatter_service = formatter_service
        self._params: BazosSkParameters

    def params(self) -> BazosSkParameters:
        return self._params

    def set_params(self, params: dict):
        """Setup the data source parameters"""
        self._params = BazosSkParameters(**params)

    def fetch_items(self) -> list[BazosSkItem]:
        """Fetch the items from the data source"""
        if not self.params():
            raise ValueError("Parameters not initialized.")

        return self._data_service.get_items(self.params())

    def get_stored_items(self, watcher_name: str) -> list[BazosSkItem]:
        """Get items currently stored in the database"""
        return self._db_service.get_stored_items(watcher_name)

    def get_formatter(self, formatter_name: str) -> Formatter:
        """Get the formatter object"""
        return self._formatter_service.get_formatter(formatter_name)

    def format_items(
        self, formatter_name: str, items: list[BazosSkItem]
    ) -> NotificationPlatformInput:
        """Format the items to string"""
        formatter = self.get_formatter(formatter_name)
        return formatter.format_items(items)
