from pydantic import BaseModel


class WatcherDataSourceModel(BaseModel):
    name: str
    formatter: str
    parameters: dict


class WatcherNotificationPlatformModel(BaseModel):
    name: str
    parameters: dict


class WatcherModel(BaseModel):
    name: str
    data_source: WatcherDataSourceModel
    notification_platform: WatcherNotificationPlatformModel
