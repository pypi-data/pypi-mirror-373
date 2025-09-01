from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import Callable
import os

from .....core.classes.formatter.formatter import Formatter
from ...models.bazos_cz_item import BazosCzItem
from .....notification_platforms.email.models.email_input import (
    EmailInput,
)
from .....core.decorators.injector import DependencyInjector as Injector
from .....core.services.db_service import CoreDbService


@Injector.inject_dependencies
class BazosCzEmailFormatter(Formatter):
    def __init__(
        self,
        *,
        db_service: CoreDbService,
        environment: Environment = None,
        template_name: str = "bazos_cz_email_template.html",
        current_time: Callable[[], datetime] = datetime.now,
    ):
        self._db_service = db_service
        if environment is None:
            template_path = os.path.join(
                os.path.dirname(__file__), "../templates"
            )
            environment = Environment(loader=FileSystemLoader(template_path))
        self.template = environment.get_template(template_name)
        self.current_time = current_time

    def format_items(self, items: list[BazosCzItem]) -> EmailInput:
        return EmailInput(
            subject="New listings on Bazos.cz",
            body=self.template.render(
                items=items, current_year=self.current_time().year
            ),
            content_type="html",
        )
