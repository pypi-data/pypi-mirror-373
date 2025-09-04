import typing as t

from meili_sdk.models.base import BaseModel
from meili_sdk.websockets.models.task import BatchedTask, Task, process_task_message

__all__ = (
    "SlowDownMessage",
    "PathReroutingMessage",
    "process_clearance_data",
    "SingleCollisionClearanceMessage",
    "CollisionClearanceMessage",
)


def process_clearance_data(message):
    if "task_data" in message:
        message["task_data"] = process_task_message(message["task_data"])
        return CollisionClearanceMessage(**message)
    return SingleCollisionClearanceMessage(**message)


class SlowDownMessage(BaseModel):
    goal_id: t.Optional[str] = None
    max_vel_x: float
    max_vel_theta: float


class PathReroutingMessage(BaseModel):
    path: t.List[t.List]
    rotation_angles: t.List


class CollisionClearanceMessage(BaseModel):
    message_type: str
    task_data: t.Union[BatchedTask, Task]


class SingleCollisionClearanceMessage(BaseModel):
    message_type: str
