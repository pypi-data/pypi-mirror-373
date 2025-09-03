from typing import Union

from pydomjudge.clients.client import _Client
from pydomjudge.models.response import Scoreboard


class ScoreboardsClient(_Client):
    def get_scoreboard(self, contest_id: Union[str, int], allteams: bool = None, category: Union[str, int] = None,
                       country: str = None, affiliation: Union[str, int] = None, public: bool = None,
                       sortorder: int = None) -> Scoreboard:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/scoreboard"
        params = {
            "allteams": allteams,
            "category": category,
            "country": country,
            "affiliation": affiliation,
            "public": public,
            "sortorder": sortorder
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Scoreboard.model_validate(response.json())