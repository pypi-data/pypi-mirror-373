from meili_sdk.models.base import BaseModel
from meili_sdk.websockets.models.task_v2 import TaskV2 as Subtask


class Preset(BaseModel):
    uuid: str
    title: str
    slug: str
    subtasks: Subtask
    vehicle_uuid: str
