from ....core.decorators.injector import DependencyInjector as Injector
from ....core.classes.formatter.formatter import Formatter
from ..formatters.config import FORMATTERS


@Injector.inject_as_singleton
class BazosSkFormatterService:
    def get_formatter(self, formatter_name: str) -> Formatter:
        """
        Retrieve a formatter instance by its name.

        Args:
            formatter_name (str): The name of the formatter to retrieve.

        Raises:
            ValueError: If the formatter with the given name is not found.

        Returns:
            Formatter: An instance of the requested formatter.
        """
        if FORMATTERS.get(formatter_name) is None:
            raise ValueError(f"Formatter {formatter_name} not found.")

        return FORMATTERS[formatter_name]()
