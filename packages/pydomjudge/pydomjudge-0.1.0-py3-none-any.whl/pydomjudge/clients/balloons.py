from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Balloon


class BalloonsClient(_Client):
    def get_all_balloons(self, contest_id: Union[str, int], todo: bool = None) -> List[Balloon]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/balloons"
        params = {
            "todo": todo
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Balloon.model_validate(balloon) for balloon in response.json()]

    def mark_balloon_done(self, contest_id: Union[str, int], balloon_id: int) -> None:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/balloons/{balloon_id}/done"
        response = self.session.post(url)
        response.raise_for_status()