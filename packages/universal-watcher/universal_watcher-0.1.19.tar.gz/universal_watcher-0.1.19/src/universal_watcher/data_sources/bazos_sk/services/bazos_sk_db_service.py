from ....core.decorators.injector import DependencyInjector as Injector
from ....core.services.db_service import CoreDbService
from ..models.bazos_sk_item import BazosSkItem


@Injector.inject_as_singleton
@Injector.inject_dependencies
class BazosSkDbService:
    def __init__(self, *, core_db_service: CoreDbService):
        self._core_db_service = core_db_service

    def get_stored_items(self, watcher_name: str) -> list[BazosSkItem]:
        items = self._core_db_service.get_watcher_items(watcher_name)
        return [BazosSkItem(**item) for item in items]
