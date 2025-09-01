from ...core.decorators.injector import DependencyInjector as Injector
from ...core.classes.data_source.data_source import DataSource
from ...core.classes.formatter.formatter import Formatter
from .services.bazos_cz_data_service import (
    BazosCzDataService,
)
from .services.bazos_cz_db_service import BazosCzDbService
from .services.bazos_cz_formatter_service import (
    BazosCzFormatterService,
)
from .models.bazos_cz_parameters import BazosCzParameters
from .models.bazos_cz_item import BazosCzItem
from ...core.classes.notification_platform.notification_platform_input import (
    NotificationPlatformInput,
)


@Injector.inject_as_singleton
@Injector.inject_dependencies
class BazosCzDataSource(DataSource):
    NAME = "bazos_cz"

    def __init__(
        self,
        *,
        data_service: BazosCzDataService,
        db_service: BazosCzDbService,
        formatter_service: BazosCzFormatterService,
    ):
        self._data_service = data_service
        self._db_service = db_service
        self._formatter_service = formatter_service
        self._params: BazosCzParameters

    def params(self) -> BazosCzParameters:
        return self._params

    def set_params(self, params: dict):
        """Setup the data source parameters"""
        self._params = BazosCzParameters(**params)

    def fetch_items(self) -> list[BazosCzItem]:
        """Fetch the items from the data source"""
        if not self.params():
            raise ValueError("Parameters not initialized.")

        return self._data_service.get_items(self.params())

    def get_stored_items(self, watcher_name: str) -> list[BazosCzItem]:
        """Get items currently stored in the database"""
        return self._db_service.get_stored_items(watcher_name)

    def get_formatter(self, formatter_name: str) -> Formatter:
        """Get the formatter object"""
        return self._formatter_service.get_formatter(formatter_name)

    def format_items(
        self, formatter_name: str, items: list[BazosCzItem]
    ) -> NotificationPlatformInput:
        """Format the items to string"""
        formatter = self.get_formatter(formatter_name)
        return formatter.format_items(items)
