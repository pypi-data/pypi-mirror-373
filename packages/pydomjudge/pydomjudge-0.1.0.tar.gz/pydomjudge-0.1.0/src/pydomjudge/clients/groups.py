from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import TeamCategory


class GroupsClient(_Client):
    def get_all_groups(self, contest_id: Union[str, int], idlist: List[str] = None, public: bool = None,
                       strict: bool = False) -> List[TeamCategory]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/groups"
        params = {
            "ids[]": idlist,
            "public": public,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [TeamCategory.model_validate(group) for group in response.json()]

    def add_group(self, contest_id: Union[str, int], group_data: dict, strict: bool = False) -> TeamCategory:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/groups"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=group_data)
        response.raise_for_status()
        return TeamCategory.model_validate(response.json())

    def get_group(self, contest_id: Union[str, int], group_id: str, strict: bool = False) -> TeamCategory:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/groups/{group_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return TeamCategory.model_validate(response.json())