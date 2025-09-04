import typing as t

from meili_sdk.models.base import BaseModel

__all__ = (
    "IndoorPoint",
    "OutdoorPoint",
    "process_task_v2_message",
    "Action",
    "TaskV2",
)


def process_task_v2_message(task_data):
    # add outdoor case
    if "subtask" in task_data:
        task = TaskV2(**task_data)
    else:
        task = None
    return task


def filter_subtask(subtask):
    # add outdoor case
    action = subtask["action"]
    return Action(**action)


class IndoorPoint(BaseModel):
    uuid: str
    x: int
    y: int
    rotation: float
    metric: t.Dict[str, int]


class OutdoorPoint(BaseModel):
    uuid: str
    location_data: t.List[float]


class Action(BaseModel):
    action_type: str
    values: dict
    point: IndoorPoint


class TaskV2(BaseModel):
    uuid: str
    subtask_uuid: str
    number: str
    action: Action
    metric_waypoints: t.List
    rotation_angles: t.Optional[t.List]
    speed_limits: t.Optional[t.List]

    def __init__(self, subtask: dict, **kwargs):
        kwargs["action"] = filter_subtask(subtask)
        kwargs["metric_waypoints"] = subtask["metric_waypoints"]
        kwargs["rotation_angles"] = subtask["rotation_angles"]
        kwargs["speed_limits"] = subtask["speed_limits"]
        kwargs["subtask_uuid"] = subtask["uuid"]

        super().__init__(**kwargs)
