from meili_sdk.models.ros_setup import RosSetup
from meili_sdk.resources.base import BaseResource


class RosSetupResource(BaseResource):
    def get_token(self, uuid) -> str:
        _, data, _, _ = self.get(f"/api/setups/{uuid}/token/")
        return data["token"]

    def regenerate_token(self, uuid) -> str:
        return self.post(f"/api/setups/{uuid}/token/", data={})["token"]

    def get_ros_setup(self, uuid: str):
        return self.get(f"/api/setups/{uuid}/", expected_class=RosSetup)
