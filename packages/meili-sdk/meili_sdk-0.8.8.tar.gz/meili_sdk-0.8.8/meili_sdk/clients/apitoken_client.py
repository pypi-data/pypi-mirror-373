import logging

from meili_sdk.clients.base import BaseAPIClient
from meili_sdk.exceptions import ResourceNotAvailable
from meili_sdk.resources.tasks import TaskResource

__all__ = ("APITokenClient",)

logger = logging.getLogger("meili")


class APITokenClient(BaseAPIClient):
    AUTHORIZATION_TOKEN_HEADER = "Bearer"  # nosec

    def __init__(self, *args, **kwargs):
        logging.warning(
            "This client is about to be deprecated, please use PersistentTokenClient instead"
        )
        super().__init__(*args, **kwargs)

    def get_ros_resources(self):
        raise ResourceNotAvailable

    def get_task_resources(self):
        return TaskResource(self)
