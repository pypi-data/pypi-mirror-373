from meili_sdk.clients.base import BaseAPIClient
from meili_sdk.resources.ros import RosSetupResource
from meili_sdk.resources.tasks import TaskResource

__all__ = ("PersistentTokenClient",)


class PersistentTokenClient(BaseAPIClient):
    AUTHORIZATION_TOKEN_HEADER = "API-Key"  # nosec

    def get_ros_resources(self):
        return RosSetupResource(self)

    def get_task_resources(self):
        return TaskResource(self)
