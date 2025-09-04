from meili_sdk.models.team import Team
from meili_sdk.resources.base import BaseResource


class TeamResource(BaseResource):
    def get_teams(self):
        return self.get("api/teams/", expected_class=Team)

    def update_team(self, team):
        return self.patch(f"api/teams/{team.uuid}/", data=team, expected_class=Team)

    def delete_team(self, team):
        return self.delete(f"api/teams/{team.uuid}/")

    def get_indoor_area_map(self, team):
        return self.get(f"api/teams/{team.uuid}/indoors/area/images/")

    def get_indoor_team_area(self, team):
        return self.get(f"api/teams/{team.uuid}/indoors/area/")


class SDKTeamResource(BaseResource):
    def get_teams(self):
        return self.get("sdk/teams/", expected_class=Team)

    def update_team(self, team):
        return self.patch(f"sdk/teams/{team.uuid}/", data=team, expected_class=Team)
