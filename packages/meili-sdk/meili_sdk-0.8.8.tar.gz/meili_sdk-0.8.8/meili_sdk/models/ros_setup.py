from meili_sdk.models.base import BaseModel


class RosSetup(BaseModel):
    uuid: str
    verbose_name: str
    pin: str
    mqtt_id: str
