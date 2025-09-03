from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Award


class AwardsClient(_Client):
    def get_all_awards(self, contest_id: Union[str, int], strict: bool = False) -> List[Award]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/awards"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Award.model_validate(award) for award in response.json()]

    def get_award(self, contest_id: Union[str, int], award_id: str, strict: bool = False) -> Award:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/awards/{award_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Award.model_validate(response.json())