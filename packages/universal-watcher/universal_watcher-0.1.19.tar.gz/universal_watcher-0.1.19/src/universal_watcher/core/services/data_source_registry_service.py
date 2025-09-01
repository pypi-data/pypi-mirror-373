from typing import Type, Union
from pydantic import BaseModel
import importlib

from ..classes.data_source.data_source import DataSource


class DataSourcesRegistryService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Creates a singleton instance of DataSourcesRegistryService.

        Initializes the data_sources list if the instance does not exist.
        """
        if cls._instance is None:
            cls._instance = super(DataSourcesRegistryService, cls).__new__(
                cls, *args, **kwargs
            )
            cls._instance._data_sources = []
        return cls._instance

    def get_data_sources(self) -> list[dict]:
        """
        Retrieves the list of registered data sources.

        Returns:
            list: A list of data source dictionaries.
        """
        return self._data_sources

    def _get_data_source_entry(self, name: str) -> Union[dict, None]:
        """
        Retrieves data for a specific data source by name.

        Args:
            name (str): The name of the data source.

        Returns:
            Union[dict, None]: The data source dictionary if found, else None.
        """
        for data_source in self.get_data_sources():
            if data_source["name"] == name:
                return data_source

        return None

    def register_data_source(
        self, name: str, cls_type: Type[DataSource]
    ) -> None:
        """
        Adds a new data source. Raises an error if a data source with the given name already exists.

        Args:
            name (str): The name of the data source.
            data_source_data (dict): The data source data to add.

        Raises:
            ValueError: If a data source with the given name already exists.
        """
        if self._get_data_source_entry(name):
            raise ValueError(
                f"A data source with the name '{name}' already exists."
            )

        self._data_sources.append({"name": name, "class": cls_type})

    def get_data_source(self, name: str) -> DataSource:
        """
        Retrieves a data source instance by name.

        Args:
            name (str): The name of the data source.

        Returns:
            Type[DataSource]: An instance of the requested DataSource.

        Raises:
            ValueError: If the data source with the given name is not found.
        """
        data = self._get_data_source_entry(name)

        if not data:
            raise ValueError(f"Data source {name} not found.")

        return data["class"]()

    def get_data_source_name(self, cls_type: Type[DataSource]) -> str:
        """
        Retrieves the name of a data source given its class type.

        Args:
            cls_type (Type[DataSource]): The class type of the data source.

        Raises:
            ValueError: If no data source with the given class type is found.

        Returns:
            str: The name of the data source.
        """
        for data_source in self.get_data_sources():
            if data_source["class"] == cls_type:
                return data_source["name"]

        raise ValueError(f"Data source {cls_type} not found.")

    def get_data_source_parameters_class(self, name: str) -> Type[BaseModel]:
        """
        Retrieves the parameters class of a data source by name.

        Args:
            name (str): The name of the data source.

        Raises:
            ValueError: If the data source with the given name is not found.

        Returns:
            Type: The class of the data source parameters.
        """
        data = self._get_data_source_entry(name)

        if not data:
            raise ValueError(f"Data source {name} not found.")

        try:
            module_path = f"universal_watcher.data_sources.{name}.models.{name}_parameters"
            module = importlib.import_module(module_path)

            class_name = (
                "".join(word.capitalize() for word in name.split("_"))
                + "Parameters"
            )

            return getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ValueError(f"Invalid data source or class name: {e}")
