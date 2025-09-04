from meili_sdk.models.trigger import Trigger
from meili_sdk.resources.base import BaseResource


class TriggerResource(BaseResource):
    def get_team_triggers(self, uuid: str):
        return self.get(f"api/teams/{uuid}/triggers/", expected_class=Trigger)

    def get_trigger(self, uuid: str):
        return self.get(f"api/triggers/{uuid}/", expected_class=Trigger)

    def create_trigger(self, uuid: str, trigger: Trigger):
        return self.post(
            f"api/teams/{uuid}/triggers/", expected_class=Trigger, data=trigger
        )

    def update_trigger(self, trigger: Trigger):
        return self.get(
            f"api/triggers/{trigger.uuid}/", data=trigger, expected_class=Trigger
        )

    def delete_trigger(self, uuid: str):
        return self.delete(f"api/trigger/{uuid}/")
