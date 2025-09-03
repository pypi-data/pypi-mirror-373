from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import Judging


class JudgementsClient(_Client):
    def get_all_judgements(self, contest_id: Union[str, int], idlist: List[str] = None, result: str = None,
                           submission_id: str = None, strict: bool = False) -> List[Judging]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgements"
        params = {
            "ids[]": idlist,
            "result": result,
            "submission_id": submission_id,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [Judging.model_validate(judgement) for judgement in response.json()]

    def get_judgement(self, contest_id: Union[str, int], judgement_id: str, strict: bool = False) -> Judging:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgements/{judgement_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return Judging.model_validate(response.json())