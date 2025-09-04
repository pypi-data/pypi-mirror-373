import typing as t

from meili_sdk.models.base import BaseModel


class Path(BaseModel):
    uuid: str
    source_point: str
    destination_point: str
    points: t.List[t.List[float]]
    corridor_width: float
    is_active: bool
    bidirectional: bool
    speed_limit: float
