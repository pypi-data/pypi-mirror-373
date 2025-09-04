import typing as t

from meili_sdk.models.base import BaseModel

__all__ = ("DockingRoutineMessage",)


class DockingRoutineMessage(BaseModel):
    uuid: str
    x: int
    y: int
    rotation: float
    metric: t.Dict[str, int]
