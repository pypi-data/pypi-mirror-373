import typing as t

from meili_sdk.models.base import BaseModel

__all__ = ("CancelTaskMessage",)


class CancelTaskMessage(BaseModel):
    task: str
    subtask: t.Optional[str] = None
    goal_id: str
