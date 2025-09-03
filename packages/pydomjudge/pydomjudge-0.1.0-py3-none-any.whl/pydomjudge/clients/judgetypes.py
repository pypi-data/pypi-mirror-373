from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import JudgementType


class JudgeTypesClient(_Client):
    def get_all_judgement_types(self, contest_id: Union[str, int], idlist: List[str] = None,
                                strict: bool = False) -> List[JudgementType]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgement-types"
        params = {
            "ids[]": idlist,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [JudgementType.model_validate(judgement_type) for judgement_type in response.json()]

    def get_judgement_type(self, contest_id: Union[str, int], judgement_type_id: str,
                           strict: bool = False) -> JudgementType:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/judgement-types/{judgement_type_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return JudgementType.model_validate(response.json())