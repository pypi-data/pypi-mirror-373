from meili_sdk.models.base import BaseModel
from meili_sdk.websockets.models.task_v2 import TaskV2 as Subtask


class ActionDefinition(BaseModel):
    uuid: str
    slug: str
    description: str
    required_object: Subtask
    device_type: str
    form: dict
    wait_for_confirmation: bool
