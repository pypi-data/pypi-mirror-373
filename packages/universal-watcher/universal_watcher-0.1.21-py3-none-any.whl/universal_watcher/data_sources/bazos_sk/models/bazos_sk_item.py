from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

from ....core.classes.data_source.data_source_item import DataSourceItem


class BazosSkItem(BaseModel, DataSourceItem):
    title: str
    price: Optional[str] = ""
    url: HttpUrl
    description: str
    pub_date: datetime

    def serialize_to_db(self) -> dict:
        return {
            "title": self.title,
            "price": self.price,
            "url": str(self.url),
            "description": self.description,
            "pub_date": self.pub_date.timestamp(),
        }
