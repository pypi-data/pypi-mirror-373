import typing as t

from meili_sdk.models.base import BaseModel

__all__ = (
    "IndoorPoint",
    "OutdoorPoint",
    "process_task_message",
    "BatchedTask",
    "Task",
)


def process_task_message(task_data):
    if "locations" in task_data:
        task = BatchedTask(**task_data)
    else:
        task = Task(**task_data)
    return task


def filter_location(location):
    if "location_data" in location:
        return OutdoorPoint(**location)
    else:
        return IndoorPoint(**location)


class IndoorPoint(BaseModel):
    uuid: str
    x: int
    y: int
    rotation: float
    metric: t.Dict[str, int]


class OutdoorPoint(BaseModel):
    uuid: str
    location_data: t.List[float]


class Task(BaseModel):
    uuid: str
    number: str
    metric_waypoints: t.List
    rotation_angles: t.Optional[t.List] = None
    location: t.Union[IndoorPoint, OutdoorPoint]

    def __init__(self, location: dict, **kwargs):
        kwargs["location"] = filter_location(location)
        super().__init__(**kwargs)


class BatchedTask(BaseModel):
    uuid: str
    number: str
    metric_waypoints: t.List
    rotation_angles: t.Optional[t.List] = None
    location: t.Union[IndoorPoint, OutdoorPoint]
    locations: t.List[t.Union[IndoorPoint, OutdoorPoint]]

    def __init__(self, location: dict, locations: t.List, **kwargs):
        kwargs["location"] = filter_location(location)
        filtered_list = []
        for location in locations:
            filtered_list.append(filter_location(location))
        kwargs["locations"] = filtered_list
        super().__init__(**kwargs)
