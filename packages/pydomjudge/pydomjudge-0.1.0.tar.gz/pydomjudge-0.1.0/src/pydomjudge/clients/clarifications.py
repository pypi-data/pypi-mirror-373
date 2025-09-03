from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Clarification
from pydomjudge.models.request import ClarificationPost


class ClarificationsClient(_Client):
    def get_all_clarifications(self, contest_id: Union[str, int], idlist: List[Union[str, int]] = None, problem: Union[str, int] = None, strict: bool = False) -> List[Clarification]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/clarifications"
        params = {
            "ids[]": idlist,
            "problem": problem,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Clarification.model_validate(clarification) for clarification in response.json()]

    def get_clarification(self, contest_id: Union[str, int], clarification_id: Union[str, int], strict: bool = False) -> Clarification:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/clarifications/{clarification_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Clarification.model_validate(response.json())

    def add_clarification(self, contest_id: Union[str, int], clarification: ClarificationPost) -> Clarification:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/clarifications"
        response = self.session.post(url, json=clarification)
        response.raise_for_status()
        return Clarification.model_validate(response.json())