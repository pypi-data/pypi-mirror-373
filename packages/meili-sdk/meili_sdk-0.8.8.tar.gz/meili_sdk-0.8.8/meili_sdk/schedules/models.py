import typing as t

from meili_sdk.exceptions import MissingAttributesException
from meili_sdk.models.base import BaseModel

__all__ = (
    "SubtaskPreset",
    "TaskPreset",
    "ScheduledTaskVehicle",
    "ScheduledTask",
)


class SubtaskPresetIndoorPoint(BaseModel):
    uuid: str
    name: str
    rotation: int
    x_coordinate: int
    y_coordinate: int
    point_type: str


class SubtaskPreset(BaseModel):
    index: int
    indoor_point: SubtaskPresetIndoorPoint

    def __init__(self, **kwargs):
        try:
            kwargs["indoor_point"] = SubtaskPresetIndoorPoint(**kwargs["indoor_point"])
        except (KeyError, TypeError):
            raise MissingAttributesException(self.__class__, ["indoor_point"])

        super().__init__(**kwargs)


class TaskPreset(BaseModel):
    uuid: str
    slug: str
    title: str
    auto_confirmation: bool
    subtasks: t.List[SubtaskPreset]

    def __init__(self, **kwargs):
        try:
            _subtasks = kwargs["subtasks"]
            subtasks = []

            for subtask in _subtasks:
                subtasks.append(SubtaskPreset(**subtask))

            kwargs["subtasks"] = subtasks
        except KeyError:
            raise MissingAttributesException(self.__class__, "subtasks")

        super().__init__(**kwargs)


class ScheduledTaskVehicle(BaseModel):
    uuid: str
    verbose_name: str


class ScheduledTask(BaseModel):
    uuid: str
    name: str
    time: str
    week_days: t.List[int]
    cron: str
    vehicle: ScheduledTaskVehicle
    task_preset: TaskPreset

    def __init__(self, **kwargs):
        for key, klass in [
            ("task_preset", TaskPreset),
            ("vehicle", ScheduledTaskVehicle),
        ]:
            try:
                _kw = kwargs.pop(key)
                kwargs[key] = klass(**_kw)
            except KeyError:
                raise MissingAttributesException(self.__class__, key)

        super().__init__(**kwargs)
