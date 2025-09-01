from tinydb import TinyDB, Query
from tinydb.table import Document
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel
from json import loads
from enum import Enum
import threading
import os

from universal_watcher.core.decorators.injector import (
    DependencyInjector as Injector,
)
from universal_watcher.core.models.watcher_model import WatcherModel
from universal_watcher.core.models.watcher_model import (
    WatcherDataSourceModel,
    WatcherNotificationPlatformModel,
)


class DbTable(str, Enum):
    WATCHERS = "watchers"
    WATCHER_DATA = "watcher_data"
    DATA_SOURCES = "data_sources"
    NOTIFICATION_PLATFORMS = "notification_platforms"


@Injector.inject_as_singleton
class CoreDbService:
    def __init__(self):
        """
        Initialize the CoreDbService with the database path and a threading lock.
        """
        env_db_path = Path(os.getenv("DB_PATH", "db.json"))
        db_path = (
            env_db_path
            if os.path.isabs(env_db_path)
            else Path(os.getcwd()) / env_db_path
        )
        self._db = TinyDB(db_path)
        self._lock = threading.Lock()

    def does_watcher_exist(self, watcher_name: str) -> bool:
        """
        Check if a watcher exists in the database.

        Args:
            watcher_name (str): The name of the watcher.

        Returns:
            bool: True if the watcher exists, False otherwise.
        """
        with self._lock:
            watcher_data = self._db.table(DbTable.WATCHERS).search(
                Query().name == watcher_name
            )

        return bool(watcher_data)

    def is_watcher_unique(self, watcher_name: str) -> bool:
        """
        Check if a watcher name is unique in the database.

        Args:
            watcher_name (str): The name of the watcher.

        Returns:
            bool: True if the watcher name is unique, False otherwise.
        """
        with self._lock:
            watcher_data = self._db.table(DbTable.WATCHERS).search(
                Query().name == watcher_name
            )

        return len(watcher_data) == 1

    def get_all_watchers_names(self) -> List[str]:
        """
        Get all watcher names stored in the database.

        Returns:
            List[str]: List of watcher names.
        """
        with self._lock:
            watchers = self._db.table(DbTable.WATCHERS).all()

        return [watcher["name"] for watcher in watchers]

    def get_watcher_data(self, watcher_name: str) -> Optional[Document]:
        """
        Retrieve watcher data by watcher name.

        Args:
            watcher_name (str): The name of the watcher.

        Returns:
            Document: The watcher data document or None if not found.

        Raises:
            ValueError: If watcher name is not unique.
        """
        if not self.does_watcher_exist(watcher_name):
            return None

        if not self.is_watcher_unique(watcher_name):
            raise ValueError(
                "Watchers must have unique names.",
                f"Found multiple watchers named {watcher_name}.",
            )

        with self._lock:
            watcher_data = self._db.table(DbTable.WATCHERS).search(
                Query().name == watcher_name
            )

        return watcher_data[0]

    def set_watcher_data(
        self,
        current_watcher_name: str,
        new_watcher_name: str,
        data_source: WatcherDataSourceModel,
        notification_platform: WatcherNotificationPlatformModel,
    ) -> None:
        """
        Sets the data source and notification platform for a specified watcher.

        This method updates the data source and notification platform for a watcher
        identified by `watcher_name`. If the watcher does not exist or if there are
        multiple watchers with the same name, it raises a ValueError.

        Args:
            current_watcher_name (str): The name of the watcher to update.
            new_watcher_name (str): The new name for the watcher.
            data_source (WatcherDataSourceModel): The data source model to set for the watcher.
            notification_platform (WatcherNotificationPlatformModel): The notification platform model to set for the watcher.

        Raises:
            ValueError: If the watcher does not exist.
            ValueError: If a watcher with the new name already exists.
        """
        if not self.does_watcher_exist(current_watcher_name):
            raise ValueError(f"Watcher {current_watcher_name} not found.")

        if (
            new_watcher_name != current_watcher_name
            and self.does_watcher_exist(new_watcher_name)
        ):
            raise ValueError("Watchers must have unique names.")

        with self._lock:
            self._db.table(DbTable.WATCHERS).upsert(
                {
                    "name": new_watcher_name,
                    "data_source": data_source.model_dump(),
                    "notification_platform": notification_platform.model_dump(),
                },
                Query().name == current_watcher_name,
            )

    def get_watcher_items(self, watcher_name: str) -> List[Document]:
        """
        Get items associated with a specific watcher.

        Args:
            watcher_name (str): The name of the watcher.

        Raises:
            ValueError: If the watcher does not exist.
            ValueError: If the watcher name is not unique.

        Returns:
            List[Document]: List of watcher items.
        """
        if not self.does_watcher_exist(watcher_name):
            raise ValueError(f"Watcher {watcher_name} not found.")

        if not self.is_watcher_unique(watcher_name):
            raise ValueError(
                "Watchers must have unique names.",
                f"Found multiple watchers named {watcher_name}.",
            )

        with self._lock:
            items = self._db.table(DbTable.WATCHER_DATA).search(
                Query().name == watcher_name
            )

        return items[0]["data"] if items else []

    def set_watcher_items(
        self, watcher_name: str, data: List[BaseModel]
    ) -> None:
        """
        Update or create watcher items in the database.

        Args:
            watcher_name (str): Name of the watcher.
            data (List[BaseModel]): List of Pydantic model objects to store.

        Raises:
            ValueError: If the watcher does not exist.
            ValueError: If the watcher name is not unique.
        """
        if not self.does_watcher_exist(watcher_name):
            raise ValueError(f"Watcher {watcher_name} not found.")

        if not self.is_watcher_unique(watcher_name):
            raise ValueError(
                "Watchers must have unique names.",
                f"Found multiple watchers named {watcher_name}.",
            )

        dict_data = [loads(item.model_dump_json()) for item in data]
        with self._lock:
            self._db.table(DbTable.WATCHER_DATA).upsert(
                {"name": watcher_name, "data": dict_data},
                Query().name == watcher_name,
            )

    def create_watcher(self, watcher_data: WatcherModel) -> None:
        """
        Create a new watcher in the database.

        Args:
            watcher_data (WatcherModel): The watcher data to store.

        Raises:
            ValueError: If the watcher already exists.
        """
        if self.does_watcher_exist(watcher_data.name):
            raise ValueError(
                f"A watcher with the name '{watcher_data.name}' already exists."
            )

        with self._lock:
            self._db.table(DbTable.WATCHERS).insert(watcher_data.model_dump())

    def get_all_watchers_data(self) -> List[Document]:
        """
        Get the data of all watchers stored in the database.

        Returns:
            List[Document]: List of watcher data documents.
        """
        with self._lock:
            watchers = self._db.table(DbTable.WATCHERS).all()

        return watchers

    def get_watcher_data_by_id(self, watcher_id: int) -> Optional[Document]:
        """
        Retrieve watcher data by watcher id.

        Args:
            watcher_id (int): The id of the watcher.

        Returns:
            Document: The watcher data document or None if not found.
        """
        with self._lock:
            watcher_data = self._db.table(DbTable.WATCHERS).get(
                doc_id=watcher_id
            )

        if not watcher_data:
            return None

        return watcher_data

    def delete_watcher(self, watcher_name: str) -> None:
        """
        Delete a watcher from the database.

        Args:
            watcher_name (str): The name of the watcher to delete.

        Raises:
            ValueError: If the watcher does not exist.
        """
        if not self.does_watcher_exist(watcher_name):
            raise ValueError(f"Watcher {watcher_name} not found.")

        with self._lock:
            self._db.table(DbTable.WATCHERS).remove(
                Query().name == watcher_name
            )
            self._db.table(DbTable.WATCHER_DATA).remove(
                Query().name == watcher_name
            )
