from meili_sdk.clients.base import BaseAPIClient
from meili_sdk.exceptions import ResourceNotAvailable
from meili_sdk.resources.forms import SDKFormResource
from meili_sdk.resources.organizations import SDKOrganizationResource
from meili_sdk.resources.tasks import SDKTaskResource
from meili_sdk.resources.teams import SDKTeamResource
from meili_sdk.resources.vehicles import SDKVehicleResource


class SDKClient(BaseAPIClient):
    AUTHORIZATION_TOKEN_HEADER = "SDK-Key"  # nosec

    def get_organization_resources(self):
        return SDKOrganizationResource(self)

    def get_team_resources(self):
        return SDKTeamResource(self)

    def get_user_resources(self):
        raise ResourceNotAvailable

    def get_vehicle_resources(self):
        return SDKVehicleResource(self)

    def get_task_resources(self):
        return SDKTaskResource(self)

    def get_form_resources(self):
        return SDKFormResource(self)

    def get_ros_resources(self):
        raise ResourceNotAvailable
