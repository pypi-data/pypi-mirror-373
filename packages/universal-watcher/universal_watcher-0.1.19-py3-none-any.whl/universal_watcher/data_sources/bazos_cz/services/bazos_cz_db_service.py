from ....core.decorators.injector import DependencyInjector as Injector
from ....core.services.db_service import CoreDbService
from ..models.bazos_cz_item import BazosCzItem


@Injector.inject_as_singleton
@Injector.inject_dependencies
class BazosCzDbService:
    def __init__(self, *, core_db_service: CoreDbService):
        self._core_db_service = core_db_service

    def get_stored_items(self, watcher_name: str) -> list[BazosCzItem]:
        items = self._core_db_service.get_watcher_items(watcher_name)
        return [BazosCzItem(**item) for item in items]
