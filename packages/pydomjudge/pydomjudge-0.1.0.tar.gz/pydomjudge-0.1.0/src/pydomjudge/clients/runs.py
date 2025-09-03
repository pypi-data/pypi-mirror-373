from typing import Union, List

from pydomjudge.clients.client import _Client
from pydomjudge.models.main import JudgingRun


class RunsClient(_Client):
    def get_all_runs(self, contest_id: Union[str, int], idlist: List[str] = None, first_id: str = None, last_id: str = None, judging_id: str = None, limit: int = None, strict: bool = False) -> List[JudgingRun]:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/runs"
        params = {
            "ids[]": idlist,
            "first_id": first_id,
            "last_id": last_id,
            "judging_id": judging_id,
            "limit": limit,
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return [JudgingRun.model_validate(run) for run in response.json()]

    def get_run(self, contest_id: Union[str, int], run_id: str, strict: bool = False) -> JudgingRun:
        url = f"{self.base_url}/api/v4/contests/{contest_id}/runs/{run_id}"
        params = {
            "strict": strict
        }
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return JudgingRun.model_validate(response.json())