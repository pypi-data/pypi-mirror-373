from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Team


class TeamsClient(_Client):
    def get_all_teams(self, contest_id: Union[str, int], idlist: List[str] = None, category: str = None,
                      affiliation: str = None, public: bool = None, strict: bool = False) -> List[Team]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams"
        params = {
            "ids[]": idlist,
            "category": category,
            "affiliation": affiliation,
            "public": public,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Team.model_validate(team) for team in response.json()]

    def get_team(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> Team:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Team.model_validate(response.json())

    def add_team(self, contest_id: Union[str, int], team_data: dict, strict: bool = False) -> Team:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams"
        params = {
            "strict": strict
        }
        response = self.session.post(url, params=params, json=team_data)
        response.raise_for_status()
        return Team.model_validate(response.json())

    def update_team(self, contest_id: Union[str, int], team_id: str, team_data: dict, strict: bool = False) -> Team:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}"
        params = {
            "strict": strict
        }
        response = self.session.put(url, params=params, json=team_data)
        response.raise_for_status()
        return Team.model_validate(response.json())

    def delete_team(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()

    def get_team_photo(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> bytes:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}/photo"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content

    def set_team_photo(self, contest_id: Union[str, int], team_id: str, photo: bytes, strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}/photo"
        params = {
            "strict": strict
        }
        files = {
            "photo": photo
        }
        response = self.session.put(url, params=params, files=files)
        response.raise_for_status()

    def delete_team_photo(self, contest_id: Union[str, int], team_id: str, strict: bool = False) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/teams/{team_id}/photo"
        params = {
            "strict": strict
        }
        response = self.session.delete(url, params=params)
        response.raise_for_status()