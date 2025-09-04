from meili_sdk.models.base import BaseModel


class Station(BaseModel):
    title: str
    uuid: str
    station_type: str
    x_coord: float
    y_coord: float
    rotation: int
